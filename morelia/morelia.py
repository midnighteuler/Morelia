# -*- coding: utf-8 -*-
#            __  __                _ _
#           |  \/  | ___  _ __ ___| (_) __ _
#           | |\/| |/ _ \| '__/ _ \ | |/ _` |
#           | |  | | (_) | | |  __/ | | (_| |
#           |_|  |_|\___/|_|  \___|_|_|\__,_|
#                             o        o     |  o
#                                 ,_       __|      ,
#                        |  |_|  /  |  |  /  |  |  / \_
#                         \/  |_/   |_/|_/\_/|_/|_/ \/

import re


 #  TODO  cron order already!

class Parser:
    def __init__(self):  
        self.thangs = [Feature, Scenario,
                                    Step, Given, When, Then, And,
                                       Row]
        self.steps = []

    def parse_file(self, filename):
        prose = open(filename, 'r').read()
        return self.parse_features(prose)

    def parse_features(self, prose):
        self.parse_feature(prose)
        
        for scene in self.steps[0].steps:
            if scene._embellish():
                scene2 = scene.copy()
                scene2.row_indices[0] += 1
                self.steps[0].steps.append(scene2)
                break
                #scene2.
                
        return self  #  TODO  what happens when these ain't scenes?

    def evaluate(self, suite):
        self.rip(TestVisitor(suite))  #  CONSIDER  rename to Viridis

    def report(self, suite):
        self.rip(ReportVisitor(suite))

    def rip(self, v):
        if self.steps != []:
            self.steps[0].evaluate_steps(v)  #  TODO  fail if it's not a Feature or Scenario

    def parse_feature(self, lines):    #  TODO  preserve and use line numbers
        for self.line in lines.split('\n'):      #  TODO  deal with pesky \r
            if not self._parse_line() and \
                    0 < len(self.steps):
                self._append_to_previous_node()
            
        return self.steps
        
    def _parse_line(self):
        self.line = self.line.rstrip()
        
        for klass in self.thangs:
            self.thang = klass()
            name = self.thang.i_look_like()
            rx = '\s*(' + name + '):?\s*(.*)'  #  TODO  Givenfoo is wrong
            m = re.compile(rx).match(self.line)

            if m and len(m.groups()) > 0:
                return self._register_line(m.groups())

    def _register_line(self, groups):
        predicate = ''
        if len(groups) > 1:  predicate = groups[1]
        node = self.thang
        node._parse(predicate, self.steps)
        self.steps.append(node)
        return node

    def _append_to_previous_node(self):   #  TODO  if it's the first one, throw a warning
        previous = self.steps[-1]
        previous.predicate += '\n' + self.line
        previous.predicate = previous.predicate.strip()


class ReportVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        print node.prefix() + node.concept + ': ' + node.predicate # TODO  if verbose


class TestVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        # print node.concept + ': ' + node.predicate # TODO  if verbose
        node.evaluate_step(self)

class Morelia:
        
    def __init__(self, predicate = '', list = []):
        self._parse(predicate, list)  #  TODO  list -> Parser

    def _parse(self, predicate, list):
        self.concept = re.sub('.*\\.', '', str(self.__class__)) # TODO strip!, & use i_look_like!
        self.predicate = predicate
        self.steps = []  #  CONSIDER  parser inherits Morelia to get this - Parser IS Feature

        for s in list[::-1]:
            if issubclass(s.__class__, self.my_parent_type()):
                s.steps.append(self)  #  TODO  squeek if can't find parent
                return

    def prefix(self):  return ''
    def my_parent_type(self):  None    

        #  TODO  all files must start with a Feature and contain only one
        
    def evaluate_steps(self, v): 
        v.visit(self)
        for step in self.steps:  step.evaluate_steps(v)
            
    def evaluate_step(self, v):  pass
    def i_look_like(self):  return re.sub('.*\\.', '', str(self.__class__))
            

class Viridis(Morelia):

    def prefix(self):  return '  '

    def find_step_name(self, suite):
        self.method = self.find_by_doc_string(suite)  #  TODO  move self.method= inside the finders
        if not self.method: self.method = self.find_by_name(suite)
        if self.method:  return self.method_name

        diagnostic = 'Cannot match step: ' + self.predicate + '\n' + \
                     'suggest:\n\n' + \
                     '    def step_' + re.sub('[^\w]+', '_', self.predicate) + '(self):\n' + \
                     '        "' + self.predicate.replace('"', '\\"') + '"\n\n' + \
                     '        # code\n\n'

        suite.fail(diagnostic)

    def find_by_name(self, suite):
        self.method_name = None
        clean = re.sub(r'[^\w]', '_?', self.predicate)
        self.matches = []
        
        for s in self.find_steps(suite, '^step_' + clean + '$'):  #  NOTE  the ^$ ain't tested
            self.method_name = s
            return suite.__getattribute__(s)
        
        return None

    def find_by_doc_string(self, suite):
        self.method_name = None
        
        for s in self.find_steps(suite, '^step_'):
            self.method_name = s
            method = suite.__getattribute__(s)
            doc = method.__doc__
            
            if doc:
                doc = re.compile('^' + doc + '$', re.MULTILINE)  #  CONSIDER deal with users who put in the ^$
                m = doc.match(self.predicate)

                if m:
                    self.matches = m.groups()
                    return method
                    
        return None

    def find_steps(self, suite, regexp):
        matcher = re.compile(regexp)
        list = []
        
        for s in dir(suite):
            if matcher.match(s):  list.append(s)

        return list

    def evaluate_step(self, v):  pass  #  TODO retire me!

    def evaluate(self, suite):  #  TODO  retire me, and quit passing suite around
        self.find_step_name(suite)
        self.method(*self.matches)


class Feature(Morelia):
    def my_parent_type(self):  return None
    def evaluate_step(self, v):  pass


class Scenario(Morelia):
    def my_parent_type(self):  return Feature

    def evaluate_steps(self, visitor):
        name = self.steps[0].find_step_name(visitor.suite)  #  TODO  squeak if there are none
        visitor.suite = visitor.suite.__class__(name)
        visitor.suite.setUp()
        Morelia.evaluate_steps(self, visitor)
        visitor.suite.tearDown()  #  TODO  ensure this!

    def _embellish(self):
        self.row_indices = []
        
        for step in self.steps:
            rowz = int(step.steps != [] and step.steps[0].__class__ is Row)
            self.row_indices.append(rowz)
        
        return self.row_indices.count(1) > 0

    def copy(self):
        scene2 = Scenario()
        scene2.concept      = self.concept
        scene2.predicate    = self.predicate
        scene2.steps          = self.steps  #  shallow copy!
        scene2.row_indices = self.row_indices[:]
        return scene2


class Step(Viridis):
    def my_parent_type(self):  return Scenario
        
    def evaluate_step(self, v):
        self.find_step_name(v.suite)
          #  TODO  prompt suggestion if method ain't found
        self.method(*self.matches)  #  TODO  setup, teardown, and nested conclusions


class Given(Step):   pass  #  TODO  distinguish these by fault signatures!
class When(Step):   pass
class Then(Step):  pass
class And(Step):  pass

class Row(Morelia):
    def i_look_like(self):  return '\\|'
    def my_parent_type(self):  return Step

#   TODO  prefix me by 2 more


if __name__ == '__main__':
    import os
    os.system('python ../tests/morelia_suite.py')   #  NOTE  this might not return the correct shell value

#  TODO  maximum munch fails - Given must start a line


