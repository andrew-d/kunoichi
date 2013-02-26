require 'kuno/step'

module Kuno
  module Steps
    class ShellStep
      extend StepExt

      register :shell

      def initialize
        @command = ''
      end

      def run(cmd, *args)
        @command = cmd
        @args = args
      end

      def build
        @command
      end

      def self.check
        true
      end
    end
  end
end
