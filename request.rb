require 'dotenv'
require 'nokogiri'
require 'yaml'
require 'json'

require 'net/http'
require 'uri'

class RateXML
  
  @@doc = File.read('query.xml')
  @@rates = YAML.load_file('rates.yml')

  def initialize(type)
    @xml = Nokogiri::XML(@@doc)
    get_credential
    make_query_xml(
      @@rates[type]['service'], 
      @@rates[type]['detail']
    )
  end

  def xml
    @xml
      .to_s
      .gsub(/\\n/, '')
      .gsub(/>\s*/, ">")
      .gsub(/\s*</, "<")
  end

  def get_credential
    creds = Dotenv.load('.env')
    node = @xml.at_xpath('RateV4Request')
    node.set_attribute('USERID', creds['USPS_USER'])
  end
  
  def make_query_xml(service, context)
    node = @xml.at_xpath('RateV4Request//Package//Service')
    node.content = service
    if context
      @xml.at_xpath('RateV4Request//Package//Service').after(
        "<#{context['type']}>
          #{context['value']}
        </#{context['type']}>"
      )
    end
  end

end

class RateQuery

  @@uri = "https://secure.shippingapis.com/ShippingAPI.dll"
  @@api = "RateV4"

  def initialize(xml)
    @query = "#{@@uri}/?API=#{@@api}&XML=#{xml}"
  end

  def query
    @query
  end

end

class API

  def initialize(uri)
    uri = URI.parse(uri)
    response = Net::HTTP.get_response(uri)
    get_rate(response.body)
  end  

  def rate
    @rate
  end

  def get_rate(response)
    xml = Nokogiri::XML(response)
    node = xml.at_xpath('RateV4Response//Package//Postage//Rate')
    @rate = node.content
  end
  
end

query = RateQuery.new(
  RateXML.new("forever").xml
).query

@rate = API.new(query).rate
puts JSON.dump(
  {
    "forever": @rate
  }
)
