#!/usr/bin/env ruby
#encoding: utf-8
require 'json'
require 'net/http'
require 'uri'

class NoSessionError < RuntimeError
end

module BiliUpload
  module_function
  @@tasklist = []
  def upload(local_filename)
    listitem = {:local => local_filename}
    begin
      open(local_filename, "r") {|f| f.read(1) } # if the local file fails, ruby will raise a exception
    rescue
      listitem[:result] = :failed
    end

    begin
      cookies = open("bilicookies","r") {|f|f.read}
    rescue Errno::ENOENT
      cookies = ""
    end
    http = Net::HTTP.new("member.bilibili.com")
    response = http.get('/get_upload_url', {"Cookie" => cookies})
    json = JSON.parse(response.body)
    if json["error_code"]
      raise NoSessionError.new(json["error_msg"])
    end
    upload_url = json["url"]
    remote_filename = json["file_name"]

    #print "> curl -F \"file=@#{local_filename};filename=#{remote_filename}\" '#{upload_url}'\n"
    IO.popen("curl -F \"file=@#{local_filename};filename=#{remote_filename}\" '#{upload_url}'") do |pipe|
      json = JSON.parse(pipe.read)
      if json["code"] == 0
        listitem[:result] = :success
        listitem[:vu] = remote_filename.split('|').first
      else
        listitem[:result] = :failed
      end
    end
    @@tasklist.push listitem
  end

  def tasklist
    @@tasklist
  end
end

begin
  ARGV.each {|file| BiliUpload.upload(file) }
ensure
  print "\n\nUpload results:\n"
  BiliUpload.tasklist.each {|h| p h }
end
