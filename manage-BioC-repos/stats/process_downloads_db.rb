#!/usr/bin/env ruby

# This script should eventually be available at
# https://hedgehog.fhcrc.org/bioconductor/trunk/bioconductor.org/scripts

# require 'sequel'
# require 'logger'
require 'yaml'
require 'open3'
require 'tempfile'
require 'fileutils'
require 'date'

# assuming we are in the same dir as the DB...

dir = "/Users/dtenenba/Downloads" # this will need to change...
dir = Dir.pwd

# turn off logging if we don't want it....
# sqlite = "sqlite://#{dir}/pkgdownloads_db.sqlite"

# DB = Sequel.connect(sqlite)#, :logger => Logger.new(STDOUT))

# access_log = DB[:access_log]

# require_relative './svn_shield_helper.rb'

#pkgs = []

# [true, false].each do |state|
#   pkgs += get_list_of_packages(state)
# end

#  access_log.distinct.select(:ips).where(package: 'a4', month_year: 'May/2015').count

now = Date.today
#last_month = now.prev_month

months = []

t = now

for i in 0..5
  t = t<<1
  months << t
end

months.reverse!

month_names = []

months.each {|i| month_names << i.strftime("%b/%Y")}


sql = ".mode csv\nselect  count(distinct ips), package from access_log where month_year in ('#{month_names.join "','"}') group by month_year, package;"

puts sql

__END__

tf = Tempfile.new('sql')
tf.write sql
tf.close

res = `cat #{tf} | sqlite3 pkgdownloads_db.sqlite`

tf.unlink

puts res
__END__

result = DB[sql].all # this takes a while

puts result


overall = {}

hh = {}
result.each {|i| hh[i[:package]] = 1 }
pkgs = hh.keys.sort_by{|w| w.downcase}

for pkg in pkgs
  hits = result.find_all{|i| i[:package] == pkg}
  if hits.empty?
    avg = 0
  else
    data = hits.map{|i| i[i.keys.sort.first]}    
    avg = data.inject(0.0) { |sum, el| sum + el } / data.size
  end
  overall[pkg] = sprintf("%0.2f", avg)
end

puts overall.to_yaml # redirect output to a file 


