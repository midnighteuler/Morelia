.. _usage-guide:

Quick usage guide
=================

Write a feature description:

.. code-block:: cucumber

    # calculator.feature

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers

    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen


Create standard python's :py:mod:`unittest` and hook Morelia into it:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import run


    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            """ Addition feature """
            run('calculator.feature', self, verbose=True)

Run test with your favourite runner: unittest, nose, py.test, trial. You name it!

.. code-block:: console

   $ python -m unittest -v test_acceptance  # or
   $ nosetests -v test_acceptance.py  # or
   $ py.test -v test_acceptance.py  # or
   $ trial test_acceptance.py  # or
   $ # django/pyramid/flask/(place for your favourite test runner)

And you'll see which steps are missing:

.. code-block:: python

    F
    ======================================================================
    FAIL: test_addition (test_acceptance.CalculatorTestCase)
    Addition feature
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "test_acceptance.py", line 45, in test_addition
        run('calculator.feature', self, verbose=True)
      File "(..)/morelia/__init__.py", line 22, in run
        return ast.evaluate(suite, **kwargs)
      File "(..)/morelia/grammar.py", line 31, in evaluate
        feature.evaluate_steps(matcher_visitor)
      File "(..)/morelia/grammar.py", line 76, in evaluate_steps
        self._method_hook(visitor, class_name, 'after_')
      File "(..)/morelia/grammar.py", line 85, in _method_hook
        method(self)
      File "(..)/morelia/visitors.py", line 125, in after_feature
        self._suite.fail(to_docstring(diagnostic))
    AssertionError: Cannot match steps:

        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'

            raise NotImplementedError('I have powered calculator on')

        def step_I_enter_number_into_the_calculator(self, number):
            r'I enter "([^"]+)" into the calculator'

            raise NotImplementedError('I enter "20" into the calculator')

        def step_I_press_add(self):
            r'I press add'

            raise NotImplementedError('I press add')

        def step_the_result_should_be_number_on_the_screen(self, number):
            r'the result should be "([^"]+)" on the screen'

            raise NotImplementedError('the result should be "140" on the screen')

    ----------------------------------------------------------------------
    Ran 1 test in 0.029s

Now implement steps with standard :py:class:`TestCases <unittest.TestCase>` that you are familiar:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import run
    

    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            """ Addition feature """
            run('calculator.feature', self, verbose=True)
    
        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            r'I enter "(\d+)" into the calculator'  # match by regexp
            self.stack.append(int(number))
    
        def step_I_press_add(self):  # matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            r'the result should be "{number}" on the screen'  # match by format-like string
            self.assertEqual(int(number), self.result)


And run it again:

.. code-block:: console

    $ python -m unittest test_acceptance

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "120" on the screen            # pass  0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.028s

    OK

Note that Morelia does not waste anyone's time inventing a new testing back-end
just to add a layer of literacy over our testage. Steps are miniature :py:class:`TestCases <unittest.TestCase>`.
Your onsite customer need never know, and your unit tests and customer tests
can share their support methods. The same one test button can run all TDD and BDD tests.
