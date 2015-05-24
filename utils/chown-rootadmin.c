/*
 * WARNING: This program allows any member of the admin group (like biocbuild)
 * to run 'chown -R root:admin' on any directory.
 * The executable obtained after compilation of this file must have its
 * ownerchip changed to root:admin and its set-user-ID-on-execution bit
 * activated before it can actually be used by a member of the admin group:
 *   gcc chown-rootadmin.c -o chown-rootadmin
 *   sudo chown root:admin chown-rootadmin
 *   sudo chmod 4750 chown-rootadmin
 * Note that we can't do this trick with a simple shell script (for
 * whatever reason it doesn't work).
 */

#include <stdio.h>
#include <unistd.h>

int main (int argc, char **argv)
{
	int ret;

	if (argc != 2) {
		fprintf(stderr, "Usage: %s <pkgdir-path>\n", argv[0]);
		return 1;
	}
/*
	ret = execl("/usr/sbin/chown", "chown", "root:admin", argv[0], (char *) 0);
	if (ret != 0) {
		fprintf(stderr, "%s executable must be owned by root:admin before\n", argv[0]);
		fprintf(stderr, "it can be used by a member of the admin group.\n");
		fprintf(stderr, "Fix this with: 'sudo chown root:admin %s'\n", argv[0]);
		return 2;
	}
	ret = execl("/usr/bin/chmod", "chmod", "4750", argv[0], (char *) 0);
	if (ret != 0) {
		fprintf(stderr, "%s executable must have its set-user-ID-on-execution bit\n", argv[0]);
		fprintf(stderr, "activated before it can be used by a member of the admin group.\n");
		fprintf(stderr, "Fix this with: 'sudo chmod 6755 %s'\n", argv[0]);
		return 3;
	}
*/
	return execl("/usr/sbin/chown", "chown", "-R", "root:admin", argv[1], (char *) 0);
}

