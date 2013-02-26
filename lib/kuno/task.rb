require 'docile'

require 'kuno/step'

module Kuno
  class Task
    def initialize(outputs)
      if outputs.instance_of?(String) then
        outputs = [outputs]
      end

      @outputs = outputs
      @steps = []
      @configs = []
    end

    def step(type=:shell, options={}, &block)
      puts "Defining step of type: #{type}"

      @steps << Docile.dsl_eval(Step.new(type), &block)
    end

    def config(&block)
      puts "Configuring task #{@name}"
      @configs << block
    end
  end
end
