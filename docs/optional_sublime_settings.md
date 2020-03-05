If you would like to Use Sublime here are some helpful settings.

[Download Sublime text 3](https://www.sublimetext.com/3)

# Set formatting:
In the Sublime menu navigate to the settings:

sublime text
 -> preferences
  -> settings
    opens a doc, on the right side I have:

    {
        "font_size": 17,
        "ignored_packages":
        [
            "Vintage"
        ],
        "spell_check": true,
        "translate_tabs_to_spaces": true,
        "trim_trailing_white_space_on_save": true,
        "word_wrap": true
    }


# Add linters
1) [Add package control](https://packagecontrol.io/installation)

2) With package control (command+shift+P) type or search for`:install package` then add each linter:

    SublimeLinter
    SublimeLinter-contrib-sass-lint
    SublimeLinter-pycodestyle
    
    follow instructions for pycodestyle. use "sudo pip3 install pycodestyle" as command line

# Set linter setting:
In the Sublime menu navigate to the sublime linter settings:

sublime text
 -> preferences
  -> package settings
    -> sublime linter

    // SublimeLinter Settings - User
    {"linters": {
            "pycodestyle": {
                "args": ["--ignore=E501"],
            }
        }
    }
