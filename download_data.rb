#!/usr/bin/env ruby

require 'rest_client'

#pageSize = 500
baseUrl = "https://gerrit-review.googlesource.com/changes/?q=project:gerrit&n=1&o=ALL_FILES&o=LABELS"
#restUri = "changes/?q=status:open+n=25"

begin
  resp = RestClient.get(baseUrl)
  if (resp.code == 200)
    File.open("data.json", "w+") do |file|
      file.write "#{resp.to_str}"
    end
  else
    STDERR.puts "Unexpected response code from REST server: #{resp.code}"
  end
rescue RestClient::ExceptionWithResponse => e
  STDERR.puts "Unexpected exception from #{thisPageURL}: #{e}"
end
