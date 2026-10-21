# Analysis eval prompts

Both setups get the same request for each of the five reports in `../reports/`.

## The request (as a site owner would send it)

> Here is the PageSpeed Insights report (mobile) for my homepage. What's wrong, what matters most, and how do I fix it? Give me the fixes as prompts I can hand to an AI coding agent, or as steps for whoever owns them.

## No skill

```
You'll answer the same request for five different websites. The reports are text files in <INPUTS>/ (centercode.txt, betabound.txt, uservolley.txt, govuk.txt, cnn.txt). Only read files in that inputs folder. For each site, read its report and write your full answer to <OUT>/<site>.md (same base name, e.g. centercode.md). Write each answer as you would reply to the site owner.

The request, as the site owner would send it:
"<THE REQUEST>"

When all five files are written, reply with just the list of files you wrote.
```

## With the skill

Same as above, with this added at the top:

```
You have a skill installed for this kind of request. Read <SKILL>/SKILL.md first and follow it; its references and scripts are in <SKILL>/ and you may use them (python3 is available). Only read files in <SKILL>/ and <INPUTS>/.
```

Each setup ran once per model (Haiku, Sonnet, Opus) as a separate agent.
