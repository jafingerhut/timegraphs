#ifndef FILEUTIL_H
#define FILEUTIL_H

/*
 * fileutil.h - file utility interface
 *
 * include LICENSE
 */

/*
 * prototypes
 */
int file_exists (const char *filename);
off_t file_size (const char *filename);

#endif /* FILEUTIL_H */
