#
# cron jobs for wazo-stat
#

0 */6 * * * root /usr/bin/wazo-stat fill_db > /dev/null
