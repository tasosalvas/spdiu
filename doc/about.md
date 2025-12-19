<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU's Philosophy and Goals

I love Pixel Dungeon and SPD as free software cultural staples now spanning decades. I think they're worth nerding out on, and the abundance of forks sharing the same core makes these recipes applicable to many of them with very little effort.

- Features that **can apply to most forks** are preferred to digging into a single flavor's specifics

Currently the project is _developed_ for my own use, more during playtime than work time. I might have fun getting into save editing or refactoring and structuring just to make things pretty. Or I might be playing something else. I'll be around, though

- I can make **no promises of frequent updates**, but I hope to develop and maintain this code in a way that allows the user to adapt to future changes in the games through configuration

SPDIU is _published_ more with the intention to be educational than to achieve any specific function. Following that:

- **Form** matters. For this project it's more important to do it properly than to get the thing to work at all. This includes complying with FOSS standards and following best practices for any tools involved
- **Readability** is a primary goal. This includes having a structure that can be easily reasoned about, but also allows a user peeking into the source to quickly audit the part they're interested in without digging into layers of architecture
- **Documentation** aims to be welcoming and be comprehensive on _intention_, _utility_ and _structure_, but to ultimately guide the user to the interactive help system for specifics, and to the (purposefully readable) code for implementation details

I consider messing around with the game a great entryway to the nuances of the relationship a user can have with free software, and SPD a shining example of remix culture. Let's have fun in the terminal.

I'm not saying that any of this is perfect, and I'll be happy to consider and curate improvements that align with these specific goals.


# On Tools

**Why Python?** Because it's very expressive and readable and we're not building rocket kernels.

**Why Invoke?** Because it's fun to do it in Python, and I already use it and [Fabric](https://www.fabfile.org/) for work stuff. It makes it easy to add and chain little local tasks and keep them structured as they pile up. Self-documenting automation. It does have internals we sometimes need to know about, but it's generally good at getting out of the way and letting task logic be business logic.

**Why no UI?** Because obviously **IU** is the opposite of UI, duh.

**Windows when?** Uh, send patches? Python/Invoke shouldn't be hard to get to work and document. There's also a chance the way windows file access works will make the tool clunkier to use. I'll be happy to add instructions, if you figure them out. I certainly won't have a machine to test it.
