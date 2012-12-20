from setuptools import setup, find_packages

setup(
    name='glamkit-blogtools',
    author='Greg Turner',
    author_email='greg@interaction.net.au',
    version='2.0.0',
    description='Mini framework for making Django blog apps.',
    url='http://github.com/ixc/glamkit-blogtools',
    packages=find_packages(),
    package_data={
        'blogtools': [
            'templates/blogtools/*.html',
            'tests/test_blog/templates/*.html',
            'tests/test_blog/templates/blogtools/*.html',
            'tests/test_blog/templates/test_blog/*.html',
            'tests/test_blog/fixtures/*.json',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)