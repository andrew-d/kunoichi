require 'docile'
require 'forwardable'

require 'kuno/group'


module Kuno
  class Build
    extend Forwardable

    def initialize
      @groups = []
      @default_group = Group.new('default')
      @groups << @default_group
    end

    def group(name, options={}, &block)
      puts "Defining a group with name: #{name}"

      group = Group.new(name, options)
      @groups << Docile.dsl_eval(group, &block)
    end

    # Delegate methods from the default task to here.
    def_delegators :@default_group, :task, :config

    def build
      # Build each group.
      @groups.each do |g|

      end
    end
  end
end
