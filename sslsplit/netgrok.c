/* -----------------------------------------------------------------------------
The netgrok() function takes input passed in from pxy_conn_ctx_new(),
pxy_bev_readcb(), and pxy_conn_ctx_free() in pxyconn.c. It then outputs info
about connection sessions in JSON format to an inter-process socket when an
SSLsplit connection context is ended.

In pxyconn.c, pxy_conn_ctx_new() is modified (at line 216) to setup a new
connection context and send it to netgrok(); pxy_bev_readcb() is modified (at
line 1843) to pass in content data buffer and size; and pxy_conn_ctx_free() is
modified (at line 253) to pass in socket addresses and transportation protocol
information.

NetGrok publishes JSON dumps only when SSLsplit sees a connection end.

The pxyconn.c file is the only C file of the original SSLsplit source that has
been modified.
----------------------------------------------------------------------------- */
#include "netgrok.h"

// definitions and global variables
// -----------------------------------------------------------------------------
// structs that store details about each connection/session
// ---------------------------------------------------------------------------
struct connection_context {
  void *pxy_conn_ctx;
  char *srchost_str;  char  *srcport_str;
  char *dsthost_str;  char  *dstport_str;
  char *protocol;     int    version;
  void *data_buf;     size_t size;
  int   direction;    int    keepalive;
};
// netgrok.h: typedef struct connection_context conn_ctx_t;

enum {DOWNSTREAM = -1, UPSTREAM = 1};

struct session {
  void *pxy_conn_ctx; // key for uthash
  struct {char *ip;    char *port;}     src;
  struct {char *ip;    char *port;}     dst;
  struct {char *name;  char *version;}  protocol;
  struct {char *start; char *end;}      date_time;
  struct {
    struct {size_t download; size_t upload;}  byte_total;
    struct {char  *name;     char  *version;} protocol;
    struct {char  *host;     char  *referer;} http;
  } app;
  UT_hash_handle hh;
};
// netgrok.h: typedef struct session sess_t;

sess_t *sessions = NULL; // the hash table that stores sessions
// ---------------------------------------------------------------------------

// string lines
// ---------------------------------------------------------------------------
static const char *LINE_END = "\r\n";
// ---------------------------------------------------------------------------

// inter-process socket for netgrok to publish its JSON dumps to
// ---------------------------------------------------------------------------
#define ENDPOINT "tcp://127.0.0.1:7188"
static void *zmq_context;
static void *publisher_socket;

// for interrupt handler
// -------------------------------------------------------------------------
#define NO_FLAGS 0
static struct sigaction signal_action;
// -------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// -----------------------------------------------------------------------------


// main NetGrok function
// -----------------------------------------------------------------------------
int netgrok(conn_ctx_t *conn_ctx) {
  sess_t *session;
  size_t  buf_len;
  char   *json_str;

  // look for the connection in the hash table of sessions
  HASH_FIND_PTR(sessions, &(conn_ctx -> pxy_conn_ctx), session);
  // if not found, create a new session and add it to the hash table
  if (session == NULL) assert(addSession(conn_ctx, session) == 0);

  // if a buffer of content data has been included, parse it for headers
  if (conn_ctx -> size > 0 && conn_ctx -> data_buf != NULL) {
    buf_len = conn_ctx -> size;
    if (buf_len > LINE_MAX_LEN) buf_len = LINE_MAX_LEN;
    assert(readHeaders(conn_ctx -> data_buf, buf_len, session) == 0);
  }

  // count the number of content bytes and keep track of the total
  if (conn_ctx -> direction != 0) switch (conn_ctx -> direction) {
    case DOWNSTREAM:
      session -> app.byte_total.download += conn_ctx -> size;
      break;
    case UPSTREAM:
      session -> app.byte_total.upload   += conn_ctx -> size;
      break;
  }

  // if received signal for end of connection
  if (conn_ctx -> keepalive == 0) {
    assert(recordTime(session -> date_time.end) == 0);
    assert(getAddresses(conn_ctx, session) == 0);
    assert(getProtocol(conn_ctx, session) == 0);

    json_str = (char *) malloc(sizeof(char) * LINE_MAX_LEN);
    assert(getJsonStr(session, json_str) == 0);
    assert(publish(json_str, strlen(json_str)) == 0);
    //printf("%s\n", json_str);
    free(json_str);

    assert(delSession(session) == 0);
  }

  return 0; // success
}
// -----------------------------------------------------------------------------


// session hash table
// -----------------------------------------------------------------------------
// add a session struct to the hash table of sessions
// ---------------------------------------------------------------------------
int addSession(conn_ctx_t *conn_ctx, sess_t *session) {
  session = (sess_t *) malloc(sizeof(sess_t));

  // recording time here because I want to get as accurate a time as possible
  session -> date_time.start = (char *) malloc(sizeof(char) * TIME_STR_LEN);
  assert(recordTime(session -> date_time.start) == 0);

  session -> pxy_conn_ctx            = conn_ctx -> pxy_conn_ctx;

  session -> src.ip                  = NULL;
  session -> src.port                = NULL;
  session -> dst.ip                  = NULL;
  session -> dst.port                = NULL;

  session -> protocol.name           = NULL;
  session -> protocol.version        = NULL;

  session -> date_time.end = (char *) malloc(sizeof(char) * TIME_STR_LEN);

  session -> app.byte_total.download = 0;
  session -> app.byte_total.upload   = 0;

  session -> app.protocol.name       = NULL;
  session -> app.protocol.version    = NULL;
  session -> app.http.host           = NULL;
  session -> app.http.referer        = NULL;

  HASH_ADD_PTR(sessions, pxy_conn_ctx, session);

  return 0;
}
// ---------------------------------------------------------------------------

// delete a session struct from the hash table of sessions, freeing up memory
// ---------------------------------------------------------------------------
int delSession(sess_t *session) {
  if (session -> app.http.referer)     free(session -> app.http.referer);
  if (session -> app.http.host)        free(session -> app.http.host);
  if (session -> app.protocol.version) free(session -> app.protocol.version);
  if (session -> date_time.end)        free(session -> date_time.end);
  if (session -> date_time.start)      free(session -> date_time.start);

  HASH_DEL(sessions, session);
  free(session);

  return 0;
}
// ---------------------------------------------------------------------------
// -----------------------------------------------------------------------------

// record the current date-time as a string
// -----------------------------------------------------------------------------
int recordTime(char *time_str) {
  time_t timer;
  struct tm time_struct;

  timer = time(NULL);
  localtime_r(&timer, &time_struct);

  // TIME_FORMAT == "%Y-%m-%d %H:%M:%S" == "yyyy-mm-dd HH:mm:ss"
  strftime(time_str, TIME_STR_LEN, TIME_FORMAT, &time_struct);

  return 0;
}
// -----------------------------------------------------------------------------

/* reads from HTTP content, checking for headers and modifying the session
struct to include the headers we're looking for (protocol, host, and referer) */
// -----------------------------------------------------------------------------
int readHeaders(void *buf, size_t bufsize, sess_t *session) {
  FILE  *content;
  char  *line;
  char   line_copy[LINE_MAX_LEN];
  char  *str, *next_str;
  size_t str_len;

  content = tmpfile();
  assert(fwrite(buf, sizeof(char), bufsize, content) == bufsize);
  rewind(content);
  line = (char *) malloc(sizeof(char) * LINE_MAX_LEN);

  static char  *headers[]     = {"http*", "host:", "referer:"};
  static size_t header_len[]  = {   5,       5,        8     };
  int           seen[]        = {   0,       0,        0     };
  static int    num_headers   = sizeof(headers) / sizeof(char *);

  enum {HTTP_HEADER = 0, HOST_HEADER = 1, REFERER_HEADER = 2};

  // parse the first token of each line to see if it is a header we care about
  while (fgets(line, LINE_MAX_LEN, content) && isprint(line[0])) {
    strncpy(line_copy, line, LINE_MAX_LEN);
    line_copy[LINE_MAX_LEN - 1] = '\0'; // line includes null terminator
    str = strtok_r(line_copy, " ", &next_str);

    int header = 0;

    // compare the first string token to each type of header we are looking for
    while (str != NULL && header < num_headers) {
      str_len = strlen(str);

      if (!seen[header] && header_len[header] <= str_len) {
        str_len = header_len[header];

        if (areSameStrings(headers[header], str, str_len)) {
          switch (header) {
            case HTTP_HEADER:
              session -> app.protocol.name = "http";
              str = strtok_r(str, "/", &next_str);
              str = strtok_r(NULL, "\0", &next_str);
              session -> app.protocol.version =
                (char *) malloc(sizeof(char) * VERSION_MAX_LEN);
              strncpy(session -> app.protocol.version, str, VERSION_MAX_LEN);
              break;

            case HOST_HEADER:
              str = strtok_r(NULL, LINE_END, &next_str);
              session -> app.http.host =
                (char *) malloc(sizeof(char) * HOST_MAX_LEN);
              strncpy(session -> app.http.host, str, HOST_MAX_LEN);
              break;

            case REFERER_HEADER:
              str = strtok_r(NULL, LINE_END, &next_str);
              session -> app.http.referer =
                (char *) malloc(sizeof(char) * REFERER_MAX_LEN);
              strncpy(session -> app.http.referer, str, REFERER_MAX_LEN);
              break;
          }

          seen[header] = 1;
          break; // found a header in this line, so go onto the next line
        }
      }

      // if an HTTP header is not yet found, parse the rest of the line
      if (!seen[HTTP_HEADER] && header == num_headers - 1) {
        str = strtok_r(NULL, " ", &next_str);
        header = 0;
      }
      else header++;
    }

    // if every header has been found, stop parsing
    if (seen[HTTP_HEADER] && seen[HOST_HEADER] && seen[REFERER_HEADER]) break;
  }

  free(line);
  fclose(content);

  return 0;
}

/* compares two strings; case insensitive; if both strings are same up to a '*'
character, the strings are considered to be the same */
// ---------------------------------------------------------------------------
int areSameStrings(const char *lhs, const char *rhs, int len) {
  for (int i = 0; i < len; i++) {
    if (tolower(lhs[i]) != tolower(rhs[i])) {
      if (lhs[i] == '*' /* || rhs[i] == '*' */) return 1; // true
      else return 0; // false
    }
  }
  return 1; // true
}
// ---------------------------------------------------------------------------
// -----------------------------------------------------------------------------

// get the source and destination socket addresses from the connection context
// -----------------------------------------------------------------------------
int getAddresses(conn_ctx_t *conn_ctx, sess_t *session) {
  session -> src.ip   = conn_ctx -> srchost_str;
  session -> src.port = conn_ctx -> srcport_str;
  session -> dst.ip   = conn_ctx -> dsthost_str;
  session -> dst.port = conn_ctx -> dstport_str;
  return 0;
}
// -----------------------------------------------------------------------------


/* seenAppProtocol() checks if NetGrok has seen any application protocol for the
session yet. This is called from outside of netgrok.c, in pxy_bev_readcb() in
pxyconn.c (at line 1869) to check if a buffer of content data is needed. It is
used in order to prevent unnecessarily copying large buffers. */
// -----------------------------------------------------------------------------
int seenAppProtocol(void *pxy_conn_ctx) {
  sess_t *session;
  HASH_FIND_PTR(sessions, &pxy_conn_ctx, session);
  if (session == NULL || session -> app.protocol.name == NULL) return 0;
  return 1;
}
// -----------------------------------------------------------------------------

/* getProtocol() is only called at the end of a connection session; it gets the
transport protocol, and changes the application layer protocol name if needed */
// -----------------------------------------------------------------------------
int getProtocol(conn_ctx_t *conn_ctx, sess_t *session) {
  enum {
    SSL2  =   2, SSL3  = 768,
    TLS10 = 769, TLS11 = 770, TLS12 = 771, TLS13 = 772
  };

  session -> protocol.name = (char *) malloc(sizeof(char) * PROTOCOL_MAX_LEN);
  strncpy(session -> protocol.name, conn_ctx -> protocol, PROTOCOL_MAX_LEN - 1);

  if (conn_ctx -> version >= SSL2) {
    if (session -> app.protocol.name) {
      if (strncmp(session -> app.protocol.name, "http", 4) == 0) {
        session -> app.protocol.name = "https";
      }
    }

    session -> app.protocol.version =
      (char *) malloc(sizeof(char) * VERSION_MAX_LEN);

    switch (conn_ctx -> version) {
      case SSL2:  session -> protocol.version = "2";   break;
      case SSL3:  session -> protocol.version = "3";   break;
      case TLS10: session -> protocol.version = "1.0"; break;
      case TLS11: session -> protocol.version = "1.1"; break;
      case TLS12: session -> protocol.version = "1.2"; break;
      case TLS13: session -> protocol.version = "1.3"; break;
      default:    session -> protocol.version = NULL;
    }
  }

  return 0;
}
// -----------------------------------------------------------------------------

// write a string (in JSON format) of information about the connection session
// -----------------------------------------------------------------------------
int getJsonStr(sess_t *session, char *json_str) {
  char *names[] = {
    "src_ip",     "src_port",
    "dst_ip",     "dst_port",
    "time_start", "time_end",
    "download",   "upload",
    "protocol",
    "host",       "referer"
  };

  char download[INT_STR_MAX_LEN]; char upload[INT_STR_MAX_LEN];
  snprintf(download, INT_STR_MAX_LEN, "%lu", session -> app.byte_total.download);
  snprintf(upload, INT_STR_MAX_LEN, "%lu", session -> app.byte_total.upload);

  char *protocol = session -> app.protocol.name;
  if (protocol == NULL) protocol = session -> protocol.name;

  char *values[] = {
    session -> src.ip,            session -> src.port,
    session -> dst.ip,            session -> dst.port,
    session -> date_time.start,   session -> date_time.end,
    download,                     upload,
    protocol,
    session -> app.http.host,     session -> app.http.referer
  };

  char buf[LINE_MAX_LEN] = "";

  strncat(buf, "{", 1);
  assert(addToJsonStr(names[0], values[0], buf) == 0);
  int num_pairs = sizeof(names) / sizeof(char *);
  for (int i = 1; i < num_pairs; i++) {
    if (values[i] != NULL && values[i][0] != '\0') {
      strncat(buf, ", ", 2);
      assert(addToJsonStr(names[i], values[i], buf) == 0);
    }
  }
  strncat(buf, "}\0", 2);

  strncpy(json_str, buf, LINE_MAX_LEN);

  return 0;
}

int addToJsonStr(char *name, char *value, char *json_str) {
  strncat(json_str, "\"", 1);
  strncat(json_str, name, strlen(name));
  strncat(json_str, "\": \"", 4);
  strncat(json_str, value, strlen(value));
  strncat(json_str, "\"", 1);
  return 0;
}
// -----------------------------------------------------------------------------

// publish using ZMQ
// -----------------------------------------------------------------------------
int publish(char *buf, int len) {
  // setup for interrupt handling
  // -------------------------------------------------------------------------
  signal_action.sa_handler = interruptHandler;
  signal_action.sa_flags = NO_FLAGS;
  sigemptyset(&signal_action.sa_mask);
  sigaction(SIGINT, &signal_action, NULL);
  sigaction(SIGTERM, &signal_action, NULL);
  // -------------------------------------------------------------------------

  if (!zmq_context) {
    zmq_context = zmq_ctx_new();
    assert(zmq_context);
  }

  if (!publisher_socket) {
    publisher_socket = zmq_socket(zmq_context, ZMQ_PUB);
    assert(publisher_socket);
    assert(zmq_bind(publisher_socket, ENDPOINT) == 0);
  }

  assert(zmq_send(publisher_socket, buf, len + 1, NO_FLAGS) == len + 1);

  return 0;
}

// clean up the ZMQ stuff if the program is stopped
// ---------------------------------------------------------------------------
void interruptHandler(int sig) {
  printf("\nsignal: %d; closing publisher socket now\n", sig);
  if (publisher_socket) zmq_close(publisher_socket);
  if (zmq_context) zmq_ctx_destroy(zmq_context);
  exit(sig);
}
// ---------------------------------------------------------------------------
// -----------------------------------------------------------------------------
