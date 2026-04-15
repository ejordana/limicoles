#!/usr/bin/env ruby
# Descarrega les imatges de Wikipedia per a cada espècie i actualitza species.yml

require 'yaml'
require 'net/http'
require 'net/https'
require 'json'
require 'uri'
require 'fileutils'

DATA_FILE  = '_data/species.yml'
IMAGES_DIR = 'assets/images/groups'

def fetch_url(url, redirects = 5)
  raise 'Massa redireccions' if redirects.zero?
  uri = URI(url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = (uri.scheme == 'https')
  http.open_timeout = 10
  http.read_timeout = 30
  res = http.get(uri.request_uri, 'User-Agent' => 'limicoles-bot/1.0')
  case res
  when Net::HTTPSuccess then res
  when Net::HTTPRedirection then fetch_url(res['location'], redirects - 1)
  else raise "HTTP #{res.code}: #{url}"
  end
end

def wiki_image_url(nom_cientific)
  title = nom_cientific.gsub(' ', '_')
  encoded = URI.encode_www_form_component(title)
  res = fetch_url("https://en.wikipedia.org/api/rest_v1/page/summary/#{encoded}")
  data = JSON.parse(res.body)
  data.dig('originalimage', 'source') || data.dig('thumbnail', 'source')
rescue => e
  puts "  [Wikipedia error] #{e.message}"
  nil
end

def extension_from_url(url)
  path = URI(url).path
  ext  = File.extname(path).downcase.split('?').first
  %w[.jpg .jpeg .png .gif .webp].include?(ext) ? ext : '.jpg'
end

data = YAML.load_file(DATA_FILE)
changed = false

data['grups'].each do |grup|
  grup_id = grup['id']
  dir = File.join(IMAGES_DIR, grup_id)
  FileUtils.mkdir_p(dir)

  grup['especies'].each do |esp|
    nom   = esp['nom']
    sci   = esp['nom_cientific']
    slug  = sci.downcase.gsub(' ', '-').gsub(/[^a-z0-9\-]/, '')

    puts "\n#{nom} (#{sci})"

    img_url = wiki_image_url(sci)
    unless img_url
      puts "  -> Sense imatge, es conserva la imatge actual"
      next
    end

    ext      = extension_from_url(img_url)
    filename = "#{slug}#{ext}"
    dest     = File.join(dir, filename)

    if File.exist?(dest)
      puts "  -> Ja existeix: #{dest}"
    else
      puts "  -> Descarregant: #{img_url}"
      img_res = fetch_url(img_url)
      File.write(dest, img_res.body, mode: 'wb')
      puts "  -> Guardat: #{dest}"
    end

    if esp['imatge'] != filename
      esp['imatge'] = filename
      changed = true
    end
  rescue => e
    puts "  -> Error: #{e.message}"
  end
end

if changed
  File.write(DATA_FILE, data.to_yaml)
  puts "\nspecies.yml actualitzat amb els nous noms de fitxer."
else
  puts "\nCap canvi al species.yml."
end

puts "\nFet!"
