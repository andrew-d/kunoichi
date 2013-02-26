require 'docile'

module Kuno
  class Step
    @@type_mappings = {}
    @@_available_mappings = nil

    class << self
      alias_method :_orig_new, :new

      def new(type, *args)
        puts "Finding step of type: #{type}"
        available_mappings[type].first.new(*args)
      end

      def register(type, klass)
        (@@type_mappings[type] ||= []) << klass
      end

      def available_mappings
        return @@_available_mappings if !@@_available_mappings.nil?

        @@_available_mappings = {}
        @@type_mappings.each do |type, arr|
          arr.each do |kls|
            if kls.check then
              (@@_available_mappings[type] ||= []) << kls
            end
          end
        end

        @@_available_mappings
      end
    end
  end

  module StepExt
    def register(type)
      Step.register(type, self)
    end
  end
end

require 'kuno/steps/shell'
