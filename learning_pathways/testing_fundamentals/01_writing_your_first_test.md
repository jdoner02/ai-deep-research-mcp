# 🧪 Writing Your First Test - Hands-On Tutorial

## Welcome to Your First Testing Adventure!

Today, you're going to write your very first software test! We'll start simple and build up to more complex examples. By the end of this tutorial, you'll understand how to verify that your code works correctly.

## 🎯 What We're Building: A Simple Math Helper

Let's imagine we're building a math helper for students. Our first function will help check if a number is even or odd - something every middle schooler learns!

## Step 1: Understanding What We Want to Test

Before writing any code, let's think about what our function should do:

```python
# This is what we want our function to do:
is_even(2) → True   # 2 is even
is_even(3) → False  # 3 is odd  
is_even(0) → True   # 0 is even (yes, really!)
is_even(-4) → True  # negative numbers count too
```

## Step 2: Write the Test First (RED Phase)

In Test-Driven Development, we write the test BEFORE we write the actual function. This might feel backwards, but it helps us think clearly about what we want.

Create a new file called `test_math_helper.py`:

```python
"""
Our first test file! 🎉

This file contains tests for our math helper functions.
Each test is like a question we ask our code:
"Hey function, if I give you this input, do you give me the right output?"
"""

def test_is_even_with_even_number():
    """
    Test that our is_even function correctly identifies even numbers.
    
    Why this test matters:
    - Even numbers should return True
    - This is the most basic case our function should handle
    - If this fails, our function is definitely broken!
    """
    # We haven't written is_even() yet, so this will fail - that's OK!
    from math_helper import is_even
    
    # Test with a simple even number
    result = is_even(4)
    assert result == True  # This should pass once we write the function
    
    # Test with zero (it's even!)
    result = is_even(0)
    assert result == True


def test_is_even_with_odd_number():
    """
    Test that our is_even function correctly identifies odd numbers.
    
    Why this test matters:
    - Odd numbers should return False
    - We need to test both positive and negative cases
    - This ensures our function works for all types of numbers
    """
    from math_helper import is_even
    
    # Test with a simple odd number
    result = is_even(3)
    assert result == False
    
    # Test with a negative odd number
    result = is_even(-7)
    assert result == False


def test_is_even_edge_cases():
    """
    Test edge cases - unusual inputs that might break our function.
    
    Why edge cases matter:
    - Real users give unexpected inputs
    - Edge cases often reveal bugs
    - Good software handles weird situations gracefully
    """
    from math_helper import is_even
    
    # Test with a large number
    result = is_even(1000000)
    assert result == True
    
    # Test with a negative even number
    result = is_even(-8)
    assert result == True
```

## Step 3: Run the Test and Watch It Fail (Still RED Phase)

Let's run our test to see it fail. This is expected and good!

```bash
# Run the test (it will fail because we haven't written the function yet)
python -m pytest test_math_helper.py -v
```

You'll see something like:
```
ImportError: No module named 'math_helper'
```

Perfect! Our test is failing because we haven't created our function yet. This is the **RED** phase of TDD.

## Step 4: Write Just Enough Code to Make the Test Pass (GREEN Phase)

Now let's create `math_helper.py` with the simplest possible solution:

```python
"""
Math Helper Functions for Students

This module contains helpful math functions that students can use
to check their work and learn about number properties.
"""

def is_even(number):
    """
    Check if a number is even.
    
    An even number is any integer that can be divided by 2 with no remainder.
    Examples: 0, 2, 4, 6, 8, 10, -2, -4, etc.
    
    Args:
        number (int): The number to check
        
    Returns:
        bool: True if the number is even, False if it's odd
        
    Examples:
        >>> is_even(4)
        True
        >>> is_even(7)
        False
        >>> is_even(0)
        True
    """
    # The simplest way to check if a number is even:
    # If number divided by 2 has no remainder, it's even
    return number % 2 == 0
```

## Step 5: Run the Test Again (GREEN Phase Success!)

```bash
python -m pytest test_math_helper.py -v
```

Now you should see:
```
test_math_helper.py::test_is_even_with_even_number PASSED
test_math_helper.py::test_is_even_with_odd_number PASSED  
test_math_helper.py::test_is_even_edge_cases PASSED

3 passed in 0.01s
```

🎉 **Congratulations! You just wrote and passed your first tests!**

## Step 6: Refactor (Make It Better)

Our code works, but can we make it clearer? Let's add some comments and maybe improve the function:

```python
def is_even(number):
    """
    Check if a number is even.
    
    This function uses the modulo operator (%) to check if a number
    divides evenly by 2. The modulo operator returns the remainder
    after division.
    
    Math explanation:  
    - 4 % 2 = 0 (no remainder, so 4 is even)
    - 5 % 2 = 1 (remainder of 1, so 5 is odd)
    
    Args:
        number (int): The number to check
        
    Returns:
        bool: True if the number is even, False if it's odd
        
    Raises:
        TypeError: If the input is not a number
    """
    # Input validation - make sure we got a number
    if not isinstance(number, (int, float)):
        raise TypeError(f"Expected a number, got {type(number).__name__}")
    
    # Convert to int in case we got a float like 4.0
    number = int(number)
    
    # Check if divisible by 2 with no remainder
    return number % 2 == 0
```

Wait! Now that we added input validation, we should test it:

```python
def test_is_even_with_invalid_input():
    """
    Test that our function properly handles invalid inputs.
    
    Why test error cases:
    - Users will inevitably give bad inputs
    - Our function should fail in a predictable way
    - Clear error messages help users fix their mistakes
    """
    from math_helper import is_even
    import pytest  # We need this to test for exceptions
    
    # Test that we get a TypeError for string input
    with pytest.raises(TypeError):
        is_even("not a number")
    
    # Test that we get a TypeError for None
    with pytest.raises(TypeError):
        is_even(None)
    
    # But floats should work fine
    assert is_even(4.0) == True
    assert is_even(3.7) == False  # 3.7 → 3 → odd
```

## 🎯 What You Just Learned

You just experienced the complete TDD cycle:

1. **🔴 RED**: Wrote a failing test first
2. **🟢 GREEN**: Wrote just enough code to make it pass  
3. **🔧 REFACTOR**: Improved the code while keeping tests green

## 🚀 Challenge: Add More Functions

Ready for a challenge? Try adding these functions to your `math_helper.py` and write tests for them:

### Challenge 1: `is_prime(number)`
A function that checks if a number is prime (only divisible by 1 and itself).

```python
def test_is_prime():
    """Test the is_prime function"""
    from math_helper import is_prime
    
    # Prime numbers
    assert is_prime(2) == True
    assert is_prime(3) == True  
    assert is_prime(7) == True
    
    # Non-prime numbers
    assert is_prime(1) == False  # 1 is not considered prime
    assert is_prime(4) == False  # 4 = 2 × 2
    assert is_prime(9) == False  # 9 = 3 × 3
```

### Challenge 2: `factorial(number)`
A function that calculates factorial (5! = 5 × 4 × 3 × 2 × 1 = 120).

```python
def test_factorial():
    """Test the factorial function"""
    from math_helper import factorial
    
    assert factorial(0) == 1  # 0! = 1 by definition
    assert factorial(1) == 1  # 1! = 1
    assert factorial(5) == 120  # 5! = 5×4×3×2×1
```

## 🎉 Wrapping Up

You've just learned the fundamentals of testing:

- ✅ How to write test functions
- ✅ How to use assertions to check results
- ✅ The RED-GREEN-REFACTOR cycle
- ✅ Why testing edge cases and errors matters
- ✅ How tests make you confident in your code

## 📚 Next Steps

- [`02_testing_patterns.md`](./02_testing_patterns.md) - Learn about different types of tests
- [`03_advanced_testing.md`](./03_advanced_testing.md) - Mocks, fixtures, and more
- Try the challenges above and write your own tests!

**Remember**: Every time you write a function, ask yourself: "How do I know this works?" Then write a test to prove it! 🧪✨
