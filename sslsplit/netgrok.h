#ifndef NETGROK_H
#define NETGROK_H

#include "uthash.h"

#include <zmq.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#include <assert.h>
#include <signal.h>

#define LINE_MAX_LEN 4096
#define IP_STR_MAX_LEN 40 // ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff.
#define INT_STR_MAX_LEN 6 // 65535.
#define PROTOCOL_MAX_LEN 12
#define VERSION_MAX_LEN 4
#define HOST_MAX_LEN 2048
#define REFERER_MAX_LEN 2048
#define TIME_STR_LEN 20
#define TIME_FORMAT "%Y-%m-%d %H:%M:%S" // yyyy-mm-dd HH:mm:ss.

typedef struct connection_context conn_ctx_t;
typedef struct session sess_t;

int netgrok(conn_ctx_t *conn_ctx);

int addSession(conn_ctx_t *conn_ctx, sess_t *session);
int delSession(sess_t *session);

int recordTime(char *time_str);

int readHeaders(void *buf, size_t bufsize, sess_t *session);
int areSameStrings(const char *lhs, const char *rhs, int len);

int getAddresses(conn_ctx_t *conn_ctx, sess_t *session);

int seenAppProtocol(void *pxy_conn_ctx);
int getProtocol(conn_ctx_t *conn_ctx, sess_t *session);

int getJsonStr(sess_t *session, char *json_str);
int addToJsonStr(char *name, char *value, char *json_str);

int publish(char *buf, int len);
void interruptHandler(int sig);

#endif /* NETGROK_H */
