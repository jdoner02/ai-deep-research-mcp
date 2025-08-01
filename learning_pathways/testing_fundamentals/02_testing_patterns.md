# 🎯 Testing Patterns - Advanced Techniques for Young Developers

## Welcome to Advanced Testing!

Now that you've written your first tests, let's explore some powerful patterns that professional developers use every day. These patterns will help you write better, more maintainable tests.

## 🏗️ The Arrange-Act-Assert (AAA) Pattern

Every good test follows this recipe:

### 📋 **ARRANGE** - Set up your test data
Get everything ready for your test, like setting up ingredients before cooking.

### ⚡ **ACT** - Perform the action you want to test  
Do the one thing you're testing, like mixing the ingredients.

### ✅ **ASSERT** - Check that it worked correctly
Verify the result is what you expected, like tasting the final dish.

Here's an example:

```python
def test_student_grade_calculation():
    """
    Test that our grade calculator works correctly.
    
    This follows the AAA pattern clearly.
    """
    # 📋 ARRANGE: Set up test data
    student = Student("Alice")
    student.add_test_score(90)
    student.add_test_score(85)
    student.add_test_score(92)
    
    # ⚡ ACT: Perform the action we're testing
    average_grade = student.calculate_average()
    
    # ✅ ASSERT: Check the result
    expected_average = (90 + 85 + 92) / 3  # 89.0
    assert average_grade == expected_average
```

## 🔄 Testing Different Scenarios with Parametrized Tests

Sometimes you want to test the same function with many different inputs. Instead of writing lots of similar tests, you can use **parametrized tests**:

```python
import pytest

@pytest.mark.parametrize("number, expected", [
    (2, True),    # 2 is even
    (3, False),   # 3 is odd
    (0, True),    # 0 is even
    (-4, True),   # -4 is even
    (-7, False),  # -7 is odd
    (100, True),  # 100 is even
])
def test_is_even_multiple_cases(number, expected):
    """
    Test is_even function with multiple inputs at once.
    
    This is like testing a calculator with many different problems
    instead of writing a separate test for each math problem.
    
    Benefits:
    - Less code duplication
    - Easy to add new test cases
    - Clear to see all the scenarios we're testing
    """
    from math_helper import is_even
    
    result = is_even(number)
    assert result == expected, f"is_even({number}) should be {expected}"
```

## 🛡️ Testing Error Cases - When Things Go Wrong

Good software doesn't crash when users give it bad input. It gives helpful error messages instead. Here's how to test that:

```python
def test_division_by_zero_gives_helpful_error():
    """
    Test that our calculator gives a good error message for division by zero.
    
    Why test errors?
    - Users WILL give bad input eventually
    - Better to handle errors gracefully than to crash
    - Clear error messages help users fix their mistakes
    """
    calculator = Calculator()
    
    # We expect this to raise a ValueError with a helpful message
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(10, 0)


def test_grade_validation():
    """
    Test that our grade system rejects invalid grades.
    
    Grades should be between 0 and 100 - anything else doesn't make sense!
    """
    student = Student("Bob")
    
    # Test negative grades
    with pytest.raises(ValueError, match="Grade must be between 0 and 100"):
        student.add_test_score(-5)
    
    # Test grades over 100
    with pytest.raises(ValueError, match="Grade must be between 0 and 100"):
        student.add_test_score(150)
    
    # But valid grades should work fine
    student.add_test_score(85)  # This should not raise an error
    assert student.test_scores[-1] == 85
```

## 🎭 Test Fixtures - Reusable Test Setup

Sometimes multiple tests need the same setup. Instead of repeating code, use **fixtures**:

```python
import pytest

@pytest.fixture
def sample_student():
    """
    Create a student with some test scores for our tests to use.
    
    This is like having a "test student" that multiple tests can borrow.
    Each test gets a fresh copy, so they don't interfere with each other.
    """
    student = Student("Test Student")
    student.add_test_score(85)
    student.add_test_score(90)
    student.add_test_score(78)
    return student


def test_student_average_with_fixture(sample_student):
    """Test average calculation using our fixture."""
    average = sample_student.calculate_average()
    expected = (85 + 90 + 78) / 3
    assert average == expected


def test_student_grade_count_with_fixture(sample_student):
    """Test grade counting using the same fixture."""
    assert len(sample_student.test_scores) == 3


@pytest.fixture
def empty_classroom():
    """Create an empty classroom for testing."""
    return Classroom("Test Classroom", max_students=20)


@pytest.fixture  
def full_classroom():
    """Create a classroom that's full of students."""
    classroom = Classroom("Full Classroom", max_students=2)
    classroom.add_student(Student("Alice"))
    classroom.add_student(Student("Bob"))
    return classroom
```

## 🎪 Mock Objects - The Art of Pretending

Sometimes your code depends on external services (like the internet, databases, or other systems). For testing, you don't want to depend on these external things - what if they're slow or broken?

**Mock objects are like actors in a play - they pretend to be the real thing for testing purposes.**

```python
from unittest.mock import Mock, patch

def test_weather_app_with_mock():
    """
    Test our weather app without depending on the real weather service.
    
    We create a "fake" weather service that always gives us predictable
    answers. This makes our test fast and reliable.
    """
    # Create a mock weather service
    mock_weather_service = Mock()
    mock_weather_service.get_temperature.return_value = 75
    mock_weather_service.get_condition.return_value = "sunny"
    
    # Test our app with the mock
    app = WeatherApp(weather_service=mock_weather_service)
    forecast = app.get_daily_forecast("New York")
    
    # Verify the app used the mock correctly
    assert "75°F" in forecast
    assert "sunny" in forecast
    mock_weather_service.get_temperature.assert_called_once_with("New York")


@patch('requests.get')  # Replace the real requests.get with a mock
def test_api_client_handles_network_error(mock_get):
    """
    Test that our API client handles network errors gracefully.
    
    We simulate a network error without actually breaking the internet!
    """
    # Make the mock simulate a network error
    mock_get.side_effect = ConnectionError("Network is down")
    
    client = APIClient()
    
    # Our client should handle the error gracefully
    result = client.fetch_data("https://api.example.com/data")
    
    assert result is None  # Should return None instead of crashing
    # Or maybe: assert "error" in result.status
```

## 🧪 Integration Testing - Testing Parts Working Together

While unit tests test individual functions, **integration tests** check that different parts of your system work together correctly:

```python
def test_complete_student_enrollment_process():
    """
    Integration test for the complete student enrollment workflow.
    
    This tests multiple components working together:
    - Student creation
    - Classroom management  
    - Grade tracking
    - Report generation
    
    It's like testing an entire assembly line instead of just one machine.
    """
    # Set up the integration environment
    school = School("Test Middle School")
    math_class = Classroom("Math 101", max_students=25)
    teacher = Teacher("Ms. Johnson")
    
    # Test the complete workflow
    student = Student("Alice")
    
    # Enroll student in school
    school.enroll_student(student)
    assert student in school.students
    
    # Add student to classroom
    math_class.add_student(student)
    assert student in math_class.students
    
    # Assign teacher
    math_class.assign_teacher(teacher)
    assert math_class.teacher == teacher
    
    # Add some grades
    teacher.add_grade(student, "Quiz 1", 85)
    teacher.add_grade(student, "Test 1", 92)
    
    # Generate report - this involves multiple systems
    report = school.generate_student_report(student)
    
    # Verify the complete integration
    assert student.name in report
    assert "Math 101" in report
    assert "85" in report  # Quiz grade should appear
    assert "92" in report  # Test grade should appear
```

## 🎯 Test Organization - Keeping Things Tidy

As your test suite grows, organization becomes important:

### 📁 File Organization
```
tests/
├── unit/              # Fast tests of individual functions
│   ├── test_math_helper.py
│   ├── test_student.py
│   └── test_classroom.py
├── integration/       # Tests of components working together  
│   ├── test_enrollment_workflow.py
│   └── test_grade_reporting.py
├── end_to_end/       # Full system tests
│   └── test_complete_scenarios.py
└── conftest.py       # Shared fixtures and configuration
```

### 🏷️ Test Naming Convention
Use descriptive names that explain what you're testing:

```python
# ❌ Bad - unclear what this tests
def test_student():
    pass

# ✅ Good - clear what scenario we're testing  
def test_student_average_calculation_with_multiple_grades():
    pass

# ✅ Even better - follows a pattern
def test_should_calculate_correct_average_when_student_has_multiple_grades():
    pass
```

### 📊 Test Categories with Markers
Use pytest markers to categorize your tests:

```python
import pytest

@pytest.mark.fast
def test_simple_math():
    """Quick unit test"""
    assert 2 + 2 == 4

@pytest.mark.slow  
@pytest.mark.integration
def test_database_integration():
    """Slower integration test"""
    # Test that involves database operations
    pass

@pytest.mark.external
def test_api_integration():
    """Test that calls external services"""
    # This might be slow or flaky
    pass
```

Then run specific categories:
```bash
# Run only fast tests during development
pytest -m fast

# Run all tests except external ones
pytest -m "not external"

# Run integration tests only
pytest -m integration
```

## 🏆 Testing Best Practices Summary

1. **Keep tests simple and focused** - One test should test one thing
2. **Use descriptive names** - Anyone should understand what the test does
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Test both happy path and error cases** - Things will go wrong!
5. **Use fixtures for common setup** - Don't repeat yourself
6. **Mock external dependencies** - Keep tests fast and reliable
7. **Organize tests logically** - Future you will thank you
8. **Write tests as documentation** - They show how your code should work

## 🚀 Practice Challenges

Ready to practice these patterns? Try these challenges:

### Challenge 1: Parametrized Testing
Write a parametrized test for a function that converts grades to letter grades:
- 90-100 → A
- 80-89 → B  
- 70-79 → C
- 60-69 → D
- Below 60 → F

### Challenge 2: Mock Testing
Create a test for a `NewsApp` that fetches headlines from an API, but mock the API calls.

### Challenge 3: Integration Testing
Test a complete library system where books can be checked out, returned, and fines calculated.

## 📚 Next Steps

- [`03_advanced_testing.md`](./03_advanced_testing.md) - Property-based testing, test doubles, and more
- [`04_testing_in_practice.md`](./04_testing_in_practice.md) - Real-world testing strategies
- Practice with our AI Deep Research MCP test suite!

Remember: **Good tests are like good instructions - they're clear, complete, and help others understand what you're building!** 🧪✨
