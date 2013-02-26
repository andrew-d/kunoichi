require 'docile'

require 'kuno/task'

module Kuno
  class Group
    def initialize(name)
      @name = name
      @tasks = []
    end

    def task(outputs, options={}, &block)
      puts "Defining task: #{outputs}"

      @tasks << Docile.dsl_eval(Task.new(outputs), &block)
    end

    def config(target=nil, &block)
      puts "Configuring target: #{target}"
    end
  end
end
