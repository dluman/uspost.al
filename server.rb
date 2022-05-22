require 'sinatra'
require 'sinatra/subdomain'

get '/' do
  'You\'ve found me out!'
end

subdomain :forever do
  get "/" do
    # I WANT THESE STAMPS FOREVER MANE, EVER MANE, EVER MANE
  end
end
