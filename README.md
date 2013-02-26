# Kunoichi

## Who

Developed by me, Andrew Dunham.

## What

A simple frontend to help generate [ninja](http://martine.github.com/ninja/) build files.

## Where

On GitHub at [http://github.com/andrew-d/kunoichi]()

## Why

Mainly, lack of wildcards.  Also, other build systems make handling multiple steps painful.  I'm trying to keep this simple and yet powerful.

## How

Check out example.py, or read the code.  It's under 200 lines long.

## Theory

A build can be decomposed into several underlying concepts:
 - A 'group' is a series of related tasks.  There is no support for dependencies among groups, or among tasks between groups.  This is useful for, e.g. compiling a bunch of external libraries that don't depend on each other
 - A 'task' is a discrete collection of steps that will generate one or more output files.  Tasks can depend on other tasks in the same group.
 - A 'step' is a single command that can be run.  Steps have a given 'type', which describes what DSL is used.  Steps can depend on other steps in the same task.

Concepts:
 - Dependencies: tasks can depend on other tasks in the same group, steps can depend on other steps in the same task
 - Configuration: one can configure all of the following:
  - General: global config options
  - Step type: configure options for a specific step type (e.g. c, c++, etc. steps)
  - Per-task configuration: e.g. look for specific libraries or header files, like autotools, or add platform-specific configuration.


Architecture:

  - Build class: The overall collection of groups, including a default group
  - Group class: A collection of tasks that can have dependencies among themselves
  - Task class: A task that contains some number of steps, and possibly some configuration
  - Step class: A class that knows how to describe a single step
