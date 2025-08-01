Installation
============

Prerequisites
------------
- Python 3.10 or higher
- pip (Python package installer)

Install from PyPI
----------------

.. code-block:: bash

   pip install devint

Install from source
------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/pyfunc/devint.git
      cd devint

2. Install with Poetry (recommended):

   .. code-block:: bash

      poetry install

   Or with pip:

   .. code-block:: bash

      pip install .

Development Installation
-----------------------

For development, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/pyfunc/devint.git
   cd devint
   poetry install --with dev

Verify Installation
------------------

To verify the installation, run:

.. code-block:: bash

   python -c "import devint; print(devint.__version__)"
