Contributing
============

We welcome contributions from the community! Here's how you can help improve devint.

Development Setup
----------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/your-username/devint.git
      cd devint

3. Set up the development environment:

   .. code-block:: bash

      poetry install --with dev
      pre-commit install

4. Create a new branch for your changes:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Code Style
----------

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide
- Use type hints for all function signatures
- Include docstrings for all public functions and classes
- Keep lines under 100 characters
- Run the following before committing:

  .. code-block:: bash

     make format  # Runs black and isort
     make lint    # Runs flake8 and mypy

Testing
-------

- Write tests for new features and bug fixes
- Ensure all tests pass before submitting a PR:

  .. code-block:: bash

     make test

- Test coverage should not decrease with new changes
- Add integration tests for new device types

Documentation
-------------

- Update documentation when adding new features
- Follow the existing documentation style
- Rebuild the docs to check for errors:

  .. code-block:: bash

     cd docs
     make html

Submitting a Pull Request
------------------------

1. Ensure all tests pass
2. Update documentation if needed
3. Push your changes to your fork
4. Create a pull request with a clear description of the changes
5. Reference any related issues
6. Wait for code review and address any feedback

Reporting Issues
---------------

When reporting issues, please include:

- Version of devint
- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or logs

Feature Requests
----------------

For feature requests, please:

1. Check if the feature already exists
2. Explain why this feature would be useful
3. Include any relevant use cases
4. Consider contributing the feature yourself

Code of Conduct
---------------

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
