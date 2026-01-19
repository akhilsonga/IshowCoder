<file path="/Users/agnos/Downloads/AGNOS/AGEditor_2/V2/LLM_context.md">

"""
<metadata>
  <total_lines>3488</total_lines>
  <lines_returned>600</lines_returned>
  <percent_of_file>17.201834862385322%</percent_of_file>
  <range>100-699</range>
  <char_count>16,874</char_count>
  <token_estimate>4,219</token_estimate>
  <file_size>244.8KB</file_size>
</metadata>

<content>
   100 |   <read dir=\"path/to/folder\" />
   101 | </file>
   102 | </tools>
   103 | ```
   104 | 
   105 | ---
   106 | 
   107 | ### SEARCH in file
   108 | 
   109 | Four search modes inside `<read>`:
   110 | 
   111 | **Exact match:**
   112 | ```xml
   113 | <tools>
   114 | <file>
   115 |   <read file=\"path/to/file.py\">
   116 |     <find>getUserById</find>
   117 |   </read>
   118 | </file>
   119 | </tools>
   120 | ```
   121 | 
   122 | **Regex pattern:**
   123 | ```xml
   124 | <tools>
   125 | <file>
   126 |   <read file=\"path/to/file.py\">
   127 |     <regex>def\\s+\\w+\\(.*\\):</regex>
   128 |   </read>
   129 | </file>
   130 | </tools>
   131 | ```
   132 | 
   133 | **Fuzzy match:**
   134 | ```xml
   135 | <tools>
   136 | <file>
   137 |   <read file=\"path/to/file.py\">
   138 |     <fuzzy>getUserByld</fuzzy>
   139 |   </read>
   140 | </file>
   141 | </tools>
   142 | ```
   143 | 
   144 | ---
   145 | 
   146 | ### CREATE file
   147 | 
   148 | ```xml
   149 | <tools>
   150 | <file>
   151 |   <create file=\"path/to/file.py\">
   152 | content goes here
   153 |   </create>
   154 | </file>
   155 | </tools>
   156 | ```
   157 | 
   158 | ---
   159 | 
   160 | ### DELETE file
   161 | 
   162 | ```xml
   163 | <tools>
   164 | <file>
   165 |   <delete file=\"path/to/file.py\" />
   166 | </file>
   167 | </tools>
   168 | ```
   169 | 
   170 | ---
   171 | 
   172 | ### EDIT file
   173 | 
   174 | **By line numbers:**
   175 | ```xml
   176 | <tools>
   177 | <file>
   178 |   <edit file=\"path/to/file.py\">
   179 |     <lines from=\"5\" to=\"10\" />
   180 |     <new>
   181 | replacement content
   182 |     </new>
   183 |   </edit>
   184 | </file>
   185 | </tools>
   186 | ```
   187 | 
   188 | **By text match:**
   189 | ```xml
   190 | <tools>
   191 | <file>
   192 |   <edit file=\"path/to/file.py\">
   193 |     <old>
   194 | exact text to find
   195 |     </old>
   196 |     <new>
   197 | replacement text
   198 |     </new>
   199 |   </edit>
   200 | </file>
   201 | </tools>
   202 | ```
   203 | 
   204 | ---
   205 | 
   206 | ## Terminal Operations
   207 | 
   208 | All shell commands go inside `<terminal>` tag.
   209 | 
   210 | ```xml
   211 | <tools>
   212 | <terminal>
   213 |   <command>npm install axios</command>
   214 |   <timeout>30000</timeout>
   215 | </terminal>
   216 | </tools>
   217 | ```
   218 | 
   219 | **Simple command (default timeout 5000ms):**
   220 | ```xml
   221 | <tools>
   222 | <terminal>
   223 |   <command>ls -la</command>
   224 | </terminal>
   225 | </tools>
   226 | ```
   227 | 
   228 | **Use terminal for:** rename, copy, move, mkdir, rmdir, git, npm, pip, etc.
   229 | 
   230 | ---
   231 | 
   232 | ## Context Operations
   233 | 
   234 | All context operations go inside `<context>` tag.
   235 | 
   236 | ### SUMMARIZE context
   237 | 
   238 | Use this to clear conversation history and generate a summary, preserving key information.
   239 | 
   240 | ```xml
   241 | <tools>
   242 | <context>
   243 |   <summarize>
   244 |     Optional instructions on what to prioritize in the summary (e.g., \"Focus on the database schema changes\").
   245 |   </summarize>
   246 | </context>
   247 | </tools>
   248 | ```
   249 | 
   250 | ---
   251 | 
   252 | ## Multiple Operations
   253 | 
   254 | For multiple edits, use multiple `<tools>` blocks:
   255 | 
   256 | ```xml
   257 | <tools>
   258 | <file>
   259 |   <edit file=\"api.py\">
   260 |     <lines from=\"10\" to=\"15\" />
   261 |     <new>
   262 | # Fixed imports
   263 | import json
   264 | import requests
   265 |     </new>
   266 |   </edit>
   267 | </file>
   268 | </tools>
   269 | 
   270 | <tools>
   271 | <file>
   272 |   <edit file=\"api.py\">
   273 |     <lines from=\"45\" to=\"50\" />
   274 |     <new>
   275 | def get_user(id):
   276 |     return db.query(User, id)
   277 |     </new>
   278 |   </edit>
   279 | </file>
   280 | </tools>
   281 | 
   282 | <tools>
   283 | <terminal>
   284 |   <command>python -m pytest api_test.py</command>
   285 |   <timeout>10000</timeout>
   286 | </terminal>
   287 | </tools>
   288 | ```
   289 | 
   290 | ---
   291 | 
   292 | ## Memory Files ([.ext].memory.md)
   293 | 
   294 | For large files, create a memory file to document your understanding.
   295 | 
   296 | ### Naming Convention
   297 | 
   298 | | Original File | Memory File |
   299 | |---------------|-------------|
   300 | | `app.py` | `app[.py].memory.md` |
   301 | | `utils.js` | `utils[.js].memory.md` |
   302 | | `config.json` | `config[.json].memory.md` |
   303 | | `archive.tar.gz` | `archive[.tar.gz].memory.md` |
   304 | | `Dockerfile` | `Dockerfile[].memory.md` |
   305 | 
   306 | ### When to Create
   307 | - File has 200+ lines
   308 | - Complex logic
   309 | - Will edit later
   310 | - Multiple functions/classes
   311 | 
   312 | ### Memory Template
   313 | ```xml
   314 | <tools>
   315 | <file>
   316 |   <create file=\"path/to/filename[.py].memory.md\">
   317 | # filename.py - Memory
   318 | 
   319 | ## Overview
   320 | Brief description of what this file does.
   321 | 
   322 | ## Structure
   323 | - **Lines 1-20:** Imports and constants
   324 | - **Lines 22-85:** Class UserAuth
   325 | - **Lines 87-150:** Helper functions
   326 | 
   327 | ## Key Functions
   328 | 
   329 | ### function_name (lines 45-67)
   330 | - Purpose: What it does
   331 | - Params: input_data (dict), user_id (int)
   332 | - Returns: processed result or None
   333 | 
   334 | ## Important Variables
   335 | - `CONFIG` (line 5): Global settings dict
   336 | 
   337 | ## Notes
   338 | - TODO found on line 89
   339 | 
   340 | ## Last Updated
   341 | [Date/context of last update]
   342 |   </create>
   343 | </file>
   344 | </tools>
   345 | ```
   346 | 
   347 | ### Workflow
   348 | 1. Check for memory file first
   349 | 2. If exists → read memory, then specific sections
   350 | 3. If not → read in chunks, create memory
   351 | 4. After edits → update memory
   352 | 
   353 | ---
   354 | 
   355 | ## System Output (Read-Only)
   356 | 
   357 | **Never write `<output>` tags.** These are system responses.
   358 | 
   359 | ### File content:
   360 | ```xml
   361 | <output type=\"file\" status=\"ok\">
   362 |   <metadata>
   363 |     <total_lines>103</total_lines>
   364 |     <lines_returned>41</lines_returned>
   365 |     <percent_of_file>39.81%</percent_of_file>
   366 |     <range>10-50</range>
   367 |     <char_count>1428</char_count>
   368 |     <token_estimate>357</token_estimate>
   369 |     <file_size>3.2KB</file_size>
   370 |   </metadata>
   371 |   <file path=\"text.py\">
   372 |    10 |     stdscr.keypad(True)
   373 |    11 |     
   374 |    12 |     height, width = stdscr.getmaxyx()
   375 |     ...
   376 |    50 |     while True:
   377 |   </file>
   378 | </output>
   379 | ```
   380 | 
   381 | ### Search results:
   382 | ```xml
   383 | <output type=\"search\" status=\"ok\">
   384 |   <metadata>
   385 |     <total_lines>450</total_lines>
   386 |     <matches>3</matches>
   387 |     <search_type>find</search_type>
   388 |     <query>getUserById</query>
   389 |   </metadata>
   390 |   <results file=\"api.py\">
   391 |     <match line=\"23\">    user = getUserById(user_id)</match>
   392 |     <match line=\"67\">def getUserById(id: int):</match>
   393 |     <match line=\"89\">        return getUserById(cached_id)</match>
   394 |   </results>
   395 | </output>
   396 | ```
   397 | 
   398 | ### Directory listing:
   399 | ```xml
   400 | <output type=\"dir\" status=\"ok\">
   401 |   <dir path=\"src\">
   402 |     📁 components/
   403 |     📁 utils/
   404 |     📄 main.py (2.1KB, 89 lines)
   405 |     📄 main[.py].memory.md (0.5KB)
   406 |   </dir>
   407 | </output>
   408 | ```
   409 | 
   410 | ### Edit success:
   411 | ```xml
   412 | <output type=\"edit\" status=\"ok\">
   413 |   Replaced lines 5-10 in parser.py
   414 | </output>
   415 | ```
   416 | 
   417 | ### Create success:
   418 | ```xml
   419 | <output type=\"create\" status=\"ok\">
   420 |   Created path/to/file.py
   421 | </output>
   422 | ```
   423 | 
   424 | ### Delete success:
   425 | ```xml
   426 | <output type=\"delete\" status=\"ok\">
   427 |   Deleted path/to/file.py
   428 | </output>
   429 | ```
   430 | 
   431 | ### Terminal output:
   432 | ```xml
   433 | <output type=\"terminal\" status=\"ok\">
   434 |   <code>0</code>
   435 |   <out>
   436 | added 150 packages in 3.2s
   437 |   </out>
   438 | </output>
   439 | ```
   440 | 
   441 | ### Error:
   442 | ```xml
   443 | <output type=\"error\" status=\"fail\">
   444 |   File not found: missing.py
   445 | </output>
   446 | ```
   447 | 
   448 | ---
   449 | 
   450 | ## Composing Operations
   451 | 
   452 | ### Append to file
   453 | Edit last line, include original + new content.
   454 | 
   455 | ### Insert at line
   456 | Edit that line, include new + original content.
   457 | 
   458 | ### Rename / Copy / Move
   459 | ```xml
   460 | <tools>
   461 | <terminal>
   462 |   <command>mv old.py new.py</command>
   463 | </terminal>
   464 | </tools>
   465 | ```
   466 | 
   467 | ### Create folder
   468 | ```xml
   469 | <tools>
   470 | <terminal>
   471 |   <command>mkdir -p path/to/folder</command>
   472 | </terminal>
   473 | </tools>
   474 | ```
   475 | 
   476 | ---
   477 | 
   478 | ## Rules
   479 | 
   480 | 1. `<tools>` = Wrapper for all commands
   481 | 2. `<file>` = All file operations (read, create, edit, delete)
   482 | 3. `<terminal>` = All shell commands
   483 | 4. `<output>` = System results (never write this)
   484 | 5. Text outside `<tools>` is shown to user
   485 | 6. Use multiple `<tools>` blocks for multiple operations
   486 | 7. For large files: read in chunks, use memory files
   487 | 
   488 | ---
   489 | 
   490 | ## Quick Reference
   491 | 
   492 | | Task | Command Structure |
   493 | |------|-------------------|
   494 | | Read file | `<tools><file><read file=\"x\" /></file></tools>` |
   495 | | Read lines | `<tools><file><read file=\"x\" from=\"1\" to=\"100\" /></file></tools>` |
   496 | | Read dir | `<tools><file><read dir=\"x\" /></file></tools>` |
   497 | | Search exact | `<tools><file><read file=\"x\"><find>text</find></read></file></tools>` |
   498 | | Search regex | `<tools><file><read file=\"x\"><regex>pattern</regex></read></file></tools>` |
   499 | | Create | `<tools><file><create file=\"x\">content</create></file></tools>` |
   500 | | Delete | `<tools><file><delete file=\"x\" /></file></tools>` |
   501 | | Edit lines | `<tools><file><edit file=\"x\"><lines from=\"\" to=\"\" /><new>...</new></edit></file></tools>` |
   502 | | Edit text | `<tools><file><edit file=\"x\"><old>...</old><new>...</new></edit></file></tools>` |
   503 | | Terminal | `<tools><terminal><command>cmd</command></terminal></tools>` |
   504 | 
   505 | ### Search Modes
   506 | 
   507 | | Tag | Mode | Example |
   508 | |-----|------|---------|
   509 | | `<find>` | Exact | `<find>getUserById</find>` |
   510 | | `<find case=\"no\">` | Case-insensitive | `<find case=\"no\">error</find>` |
   511 | | `<regex>` | Pattern | `<regex>def\\s+\\w+</regex>` |
   512 | | `<glob>` | Wildcard | `<glob>*Handler*</glob>` |
   513 | | `<fuzzy>` | Approximate | `<fuzzy>getUsrById</fuzzy>` |
   514 | 
   515 | ---
   516 | 
   517 | ## Full Example
   518 | 
   519 | **User:** \"Fix the parse_json error handling in utils/parser.py\"
   520 | 
   521 | **You:**
   522 | ```
   523 | Let me check for a memory file first.
   524 | 
   525 | <tools>
   526 | <file>
   527 |   <read file=\"utils/parser[.py].memory.md\" />
   528 | </file>
   529 | </tools>
   530 | ```
   531 | 
   532 | **System:**
   533 | ```xml
   534 | <output type=\"error\" status=\"fail\">
   535 |   File not found: utils/parser[.py].memory.md
   536 | </output>
   537 | ```
   538 | 
   539 | **You:**
   540 | ```
   541 | No memory file. Let me search for error handling.
   542 | 
   543 | <tools>
   544 | <file>
   545 |   <read file=\"utils/parser.py\">
   546 |     <regex>except.*:|try:</regex>
   547 |   </read>
   548 | </file>
   549 | </tools>
   550 | ```
   551 | 
   552 | **System:**
   553 | ```xml
   554 | <output type=\"search\" status=\"ok\">
   555 |   <metadata>
   556 |     <matches>2</matches>
   557 |     <search_type>regex</search_type>
   558 |   </metadata>
   559 |   <results file=\"utils/parser.py\">
   560 |     <match line=\"45\">    try:</match>
   561 |     <match line=\"47\">    except Exception:</match>
   562 |   </results>
   563 | </output>
   564 | ```
   565 | 
   566 | **You:**
   567 | ```
   568 | Found it. Reading that section.
   569 | 
   570 | <tools>
   571 | <file>
   572 |   <read file=\"utils/parser.py\" from=\"43\" to=\"52\" />
   573 | </file>
   574 | </tools>
   575 | ```
   576 | 
   577 | **System:**
   578 | ```xml
   579 | <output type=\"file\" status=\"ok\">
   580 |   <metadata>
   581 |     <total_lines>450</total_lines>
   582 |     <lines_returned>10</lines_returned>
   583 |     <percent_of_file>2.22%</percent_of_file>
   584 |     <range>43-52</range>
   585 |   </metadata>
   586 |   <file path=\"utils/parser.py\">
   587 |    43 | def parse_json(data):
   588 |    44 |     \"\"\"Parse JSON string.\"\"\"
   589 |    45 |     try:
   590 |    46 |         return json.loads(data)
   591 |    47 |     except Exception:
   592 |    48 |         return None
   593 |    49 | 
   594 |    50 | def parse_xml(data):
   595 |   </file>
   596 | </output>
   597 | ```
   598 | 
   599 | **You:**
   600 | ```
   601 | Improving the error handling.
   602 | 
   603 | <tools>
   604 | <file>
   605 |   <edit file=\"utils/parser.py\">
   606 |     <lines from=\"45\" to=\"48\" />
   607 |     <new>
   608 |     try:
   609 |         return json.loads(data)
   610 |     except json.JSONDecodeError as e:
   611 |         raise ValueError(f\"Invalid JSON at position {e.pos}: {e.msg}\")
   612 |     </new>
   613 |   </edit>
   614 | </file>
   615 | </tools>
   616 | ```
   617 | 
   618 | **System:**
   619 | ```xml
   620 | <output type=\"edit\" status=\"ok\">
   621 |   Replaced lines 45-48 in utils/parser.py
   622 | </output>
   623 | ```
   624 | 
   625 | **You:**
   626 | ```
   627 | Now creating memory file.
   628 | 
   629 | <tools>
   630 | <file>
   631 |   <create file=\"utils/parser[.py].memory.md\">
   632 | # parser.py - Memory
   633 | 
   634 | ## Overview
   635 | JSON and XML parsing utilities.
   636 | 
   637 | ## Structure
   638 | - **Lines 1-15:** Imports
   639 | - **Lines 43-52:** parse_json (has error handling)
   640 | - **Lines 54-95:** parse_xml
   641 | 
   642 | ## Key Functions
   643 | 
   644 | ### parse_json (lines 43-52)
   645 | - Purpose: Parse JSON string to dict
   646 | - Errors: Raises ValueError with details
   647 | 
   648 | ## Last Updated
   649 | Fixed error handling - now raises ValueError instead of returning None
   650 |   </create>
   651 | </file>
   652 | </tools>
   653 | ```
   654 | 
   655 | **System:**
   656 | ```xml
   657 | <output type=\"create\" status=\"ok\">
   658 |   Created utils/parser[.py].memory.md
   659 | </output>
   660 | ```
   661 | 
   662 | **You:**
   663 | ```
   664 | Done! Improved error handling in `parse_json` - now raises `ValueError` with position details instead of silently returning `None`.
   665 | ```
   666 | 
   667 | PWD: /Users/agnos/Downloads/AGNOS/AGEditor_2/V2
   668 | "
   669 |   },
   670 |   {
   671 |     "role": "user",
   672 |     "content": "go to AGEDITOR ewpo read all files and explain"
   673 |   },
   674 |   {
   675 |     "role": "system",
   676 |     "content": "<runtime_stats>
   677 |   <tools_called>16</tools_called>
   678 |   <messages>39</messages>
   679 |   <tools>
   680 |     <file_read>7</file_read>
   681 |     <dir_read>1</dir_read>
   682 |     <file_create>0</file_create>
   683 |     <file_edit_lines>0</file_edit_lines>
   684 |     <file_edit_text>0</file_edit_text>
   685 |     <file_delete>0</file_delete>
   686 |     <terminal_command>8</terminal_command>
   687 |   </tools>
   688 |   <context>
   689 |     <tokens_used_est>61183</tokens_used_est>
   690 |     <tokens_max>70000</tokens_max>
   691 |     <tokens_remaining_est>8817</tokens_remaining_est>
   692 |     <percent_used>87.40</percent_used>
   693 |   </context>
   694 | </runtime_stats>"
   695 |   },
   696 |   {
   697 |     "role": "assistant",
   698 |     "content": "I'll help you explore the AGEDITOR directory and read all the files to understand what's there. Let me start by checking the current directory and then navigating to AGEDITOR.
   699 | <tools>

[+ 2789 Lines] (700 - 3488) still available
</content>

</file>
"""