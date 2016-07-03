#ifndef MSG_LOG_H
#define MSG_LOG_H

#include <stdio.h>
#include <stdlib.h>

/*
 * gettext support
 *  msglog.h must follow config.h
 */

#if ENABLE_NLS
#include <libintl.h>
#else
#define gettext(msgid) (msgid)
#define textdomain(domain)
#define bindtextdomain(domain, dir)
#endif

#define _(msgid) gettext (msgid)
#define gettext_noop(msgid) msgid
#define N_(msgid) gettext_noop (msgid)


enum _debugLevelInfo {
   DBG_1 = (1 << 1),
   DBG_2 = (1 << 2),
   DBG_3 = (1 << 3),
   DBG_4 = (1 << 4),
   DBG_5 = (1 << 5),
   DBG_6 = (1 << 6),
   DBG_7 = (1 << 7),
   DBG_8 = (1 << 8),		/* sockcon */
   DBG_9 = (1 << 9),
   DBG_10 = (1 << 10),
   DBG_11 = (1 << 11),
   DBG_12 = (1 << 12),
   DBG_13 = (1 << 13),
   DBG_14 = (1 << 14),		/* message dump */
   DBG_15 = (1 << 15),		/* lex */
};

typedef int (*MsgFunc) (int type, const char *s);	/* display func proto */

typedef struct _MsgLogData MsgLogData;

struct _MsgLogData {
   FILE *msg_fd;
   FILE *dbg_fd;   /* debug message file desc */
   char *msg_progname;
   int msg_flags;
   int msg_verbose_level;
   int msg_dbg_msk;
   int msg_dump_msk;
   char *msg_filename;
   int log_facility;		/* storage for facility used in syslog */
   int logger_is_open;		/* set if openlog has been called */
   MsgFunc msg_displayFunc;
};

/*
 * external variables should be declared in main as global !
 */
extern int prog_debug;
extern MsgLogData *msglogp;	/* global pointeur to MsgLogData in main */


/*
 * macros used to print messages
 *   msg_dbg     : print a debug message normally used in development
 *   msg_info    : print an informationnal message
 *   msg_warning : print a warning message
 *   msg_error   : print a error message. Let the programmer to decide
 *   msg_fatal   : print a error message and exit
 *
 */

/*
 * Same macros with selective level or bit mask for debug
 *   msg_dbgl     : print a debug message normally used in development
 *                  a bit mask can be allocated to a part of the program.
 *   msg_infol    : print an informatonnal message
 *   msg_warningl : print a warning message
 *   msg_errorl   : print a error message. Let the programmer to decide
 *
 */


enum _msg_fmt_info {
   MSG_F_DATE = (1 << 0),
   MSG_F_PROG = (1 << 1),
   MSG_F_TYPE = (1 << 2),
   MSG_F_FILE = (1 << 3),
   MSG_F_FUNC = (1 << 4),
   MSG_F_FOLD = (1 << 5),
   MSG_F_COLOR = (1 << 6),
   MSG_F_SIGNAL = (1 << 7),	/* signal exit to parent */
   MSG_F_OVERWRITE = (1 << 8),	/* overwrite log file, default is append */
   MSG_F_NO_DATE = MSG_F_PROG | MSG_F_TYPE | MSG_F_FILE | MSG_F_FUNC,
   MSG_F_ALL =
       MSG_F_DATE | MSG_F_PROG | MSG_F_TYPE | MSG_F_FILE | MSG_F_FUNC,
};

enum _msg_type_info {
   MSG_T_DEBUG = 0,
   MSG_T_INFO,
   MSG_T_WARNING,
   MSG_T_ERROR,
   MSG_T_FATAL,
};


#ifdef MSG_DEBUG
#define msg_dbgl(msk, fmt, args...)  \
   if ( prog_debug ) { \
   private_message( msk, MSG_T_DEBUG, __func__, __FILE__, __LINE__, fmt, ## args) ;\
   }
#define msg_dbg(fmt, args...)  \
   if ( prog_debug ) { \
   private_message( 1, MSG_T_DEBUG, __func__, __FILE__, __LINE__, fmt, ## args) ;\
   }
#define msg_set_dbg_msk(msk) \
    private_msg_set_dbg_msk(msk);
#define msg_set_dbg_msk_str(str) \
    private_msg_set_dbg_msk_str(str);
#else
#define msg_dbgl(msk, fmt, args...)
#define msg_dbg(fmt, args...)
#define msg_set_dbg_msk(msk)
#define msg_set_dbg_msk_str(str)
#endif

#ifdef MSG_DUMP
#define msg_set_dump_msk(msk) \
    private_msg_set_dump_msk(msk);
#define msg_dump(buf,len,start,fd,fmt,args...) \
   private_msg_dump(1,buf,len,start,fd,fmt, ## args) ;
#define msg_dumpl(msk,buf,len,start,fd,fmt,args...) \
   private_msg_dump(msk,buf,len,start,fd,fmt, ## args) ;
#else
#define msg_set_dump_msk(msk)
#define msg_dump(buf,len,start,fd,fmt,args...)
#define msg_dumpl(msk,buf,len,start,fd,fmt,args...)
#endif

#define msg_info(fmt, args...)  \
   private_message(1, MSG_T_INFO, __func__, __FILE__, __LINE__, fmt, ## args)

#define msg_infol(level, fmt, args...)  \
   private_message(level, MSG_T_INFO, __func__, __FILE__, __LINE__, fmt, ## args)

#define msg_warning(fmt, args...)  \
   private_message(1, MSG_T_WARNING, __func__, __FILE__, __LINE__, fmt, ## args)

#define msg_warningl(level, fmt, args...)  \
   private_message(level, MSG_T_WARNING, __func__, __FILE__, __LINE__, fmt, ## args)

#define msg_error(fmt, args...)  \
   private_message(1, MSG_T_ERROR, __func__, __FILE__, __LINE__, fmt, ## args)

#define msg_errorl(level, fmt, args...)  \
   private_message(level, MSG_T_ERROR, __func__, __FILE__, __LINE__, fmt, ## args)

/*
 *  exit(1) is here to avoid a compiler message when no return after a
 *   msg_fatal. Exit will call msg_atexit.
 */
#define msg_fatal(fmt, args...)  \
   { private_message(0, MSG_T_FATAL, __func__, __FILE__, __LINE__, fmt, ## args); \
      exit(1);}

void private_msg_set_dbg_msk(int msk);
unsigned int private_msg_set_dbg_msk_str(char *p);
void private_msg_dump(int level, char *buf, int len, int start, FILE *fd,
                      char *fmt, ... );
void private_message(int level, int msgtype, const char *func,
		     char *file, int line, char *fmt, ...);

void msg_initlog(char *name, int flags, char *filename,
		 MsgFunc displayFunc);
void msg_set_func(MsgFunc displayFunc);
void msg_set_flags(int flags);
int msg_get_level(void);
void msg_set_level(int level);
void private_msg_set_dbg_msk(int msk);
void private_msg_set_dump_msk(int msk);
unsigned int private_msg_set_dbg_msk_str(char *str);
FILE *msg_openlog(char *filename, char *mode);
FILE *msg_get_msg_fd(void);
void msg_closelog(void);
void msg_atexit(void);

extern const char *msg_day_of_week[];
extern const char *msg_month_of_year[];

#endif				/* MSG_LOG_H */
