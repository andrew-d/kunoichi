# -*- encoding: utf-8 -*-
$:.push File.expand_path("../lib", __FILE__)
require "kuno/version"

Gem::Specification.new do |s|
  s.name        = "kuno"
  s.version     = Kunoichi::VERSION
  s.platform    = Gem::Platform::RUBY
  s.authors     = ["Andrew Dunham"]
  s.email       = ["andrew@du.nham.ca"]
  s.homepage    = ""
  s.summary     = %q{An extensible build system}
  s.description = %q{An extensible build system.  Acts as a frontend/wrapper to the Ninja build system.}

  # s.add_runtime_dependency ""
  # s.add_development_dependency "", "~>"

  s.files         = `git ls-files`.split("\n")
  s.test_files    = `git ls-files -- {test,spec,features}/*`.split("\n")
  s.executables   = `git ls-files -- bin/*`.split("\n").map{ |f| File.basename(f) }
  s.require_paths = ["lib"]
end

