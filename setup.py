import setuptools

setuptools.setup(
    name= "Spectro",
    version= "1.4.0-beta",
    description= "Spectro is a lightweight app for visualization of AUX audio input.",
    long_description= open('docs/README.pypi.md').read(),
    long_description_content_type= "text/markdown",
    author= "nullvideo",
    author_email= "bsantanu381@gmail.com",
    url= "https://github.com/nullvideo/spectro",
    packages= setuptools.find_packages(),
    license= "MIT",
    python_requires= ">3.6"
)