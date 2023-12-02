# greetings

This is a small project intended to automate a [1541 Ultimate-II](https://1541u-documentation.readthedocs.io/en/latest/index.html) for a [small art installation](https://modernduck.com/2023/11/greetings/).

![Photo of the art installation](https://modernduck.com/wp-content/uploads/2023/11/20231127_182654-scaled.jpg)

It's unlikely to be of general use as-is, but is presented here to give an example of how to automatically control a 1541U via its telnet interface.
The author does not intend to do any further work on this code (especially given that a REST interface is planned for the next version of the 1541U firmware), but welcomes merge requests from the community.

## Limitations

The telnet wrapper uses [pyte](https://github.com/selectel/pyte/) to manage a virtual terminal screen that can then be searched for the appropriate text.
Since pyte does not currently support ANSI colour (used by the 1541U to indicate which menu item is selected), we often have to guess.
This means that the programmer has to be very careful to track where they are in the menus, and makes the resulting code somewhat fragile.
(An `expect_white_text` method was added to partially address this.)

Also, C64 line drawing characters are not supported in pyte, so it's impossible to reliably detect where submenus begin.
As a workaround, the `down_to_string` function that scrolls within menus takes the starting line of the menu.
This is also somewhat fragile.

If you're interested in working with the telnet wrapper, the author strongly recommends enhancing pyte to support ANSI colour and line drawing characters, then using these features in the telnet wrapper.

Please see [the issue tracker](https://gitlab.com/scjody/greetings/-/issues) for other known issues and limitations.

## General notes

Two options are available to make sure the 1514U is done drawing the screen, which should be done before interacting with it:
* [`consume_to_timeout`](https://gitlab.com/scjody/greetings/-/blob/fc1502829099017c7d1f05aaeeace6ed3b789e85/ultelnet.py#L186) is the most reliable since it waits for a configurable amount of time (in practice, the default of 1s has always been enough).
However, it slows down the code for obvious reasons.
* [`expect_screen_draw`](https://gitlab.com/scjody/greetings/-/blob/fc1502829099017c7d1f05aaeeace6ed3b789e85/ultelnet.py#L173) waits for a full screen draw by waiting for a "move" to position 23,1.
This works well enough in practice (and is faster than `consume_to_timeout`) but is obviously fairly fragile.

Better designs are of course possible!
Merge requests welcome!
