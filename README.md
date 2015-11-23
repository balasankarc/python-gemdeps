# pygemdeps
Python program to find the dependencies of a Ruby application

## Usage
```python pygemdeps.py [-h] [--html] [--pdf] inputtype{gemfile,gemspec,gem_name} input appname```

> positional arguments:  
>   inputtype&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Type of input. Values can be either of {gemfile,gemspec,gem_name}  
>   input&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Input path of gemfile or gemspec file or name of the gem
>   appname&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name of the application
> 
> optional arguments:  
>   -h, --help&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show this help message and exit  
>   --html&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Use this option if you want HTML progressbar  
>   --pdf&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Use this option if you want pdf dependency graph

## Copyright
2015 Balasankar C \<balasankarc@autistici.org>

## License
GNU GPL-3+
