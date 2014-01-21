#
# cron jobs for xivo-stat
#

0 */6 * * * root /usr/bin/xivo-stat fill_db >> /dev/null
