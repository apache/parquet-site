require 'rubygems'
require 'rake/clean'
require 'fileutils'

task :default => [:build, :clean]
 
CLEAN.include "**/.DS_Store"

desc "Build the website from source"
task :build do
  puts "Building website from static source"
  result = system("middleman build --clean")
  if result 
    puts "Successfully generated the site, please commit your changes"
  else
    puts "An error was encountered when generating the site"
  end
end

desc "Run the site in development mode. Preview available at http://localhost:4567/"
task :dev do
  system("middleman server")
end
