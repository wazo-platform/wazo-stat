#
# cron jobs for wazo-stat
#

30 */6 * * * root /usr/bin/wazo-stat fill_db > /dev/null
