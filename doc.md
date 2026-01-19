<tools>
<file>
  <edit file="/Users/agnos/Downloads/AGNOS/AGEditor_2/V2/Backend/text.py">
        <old>
Line 5 in 5th line
Line 6 in 6th line
Line 7 in 7th line
Line 8 in 8th line
Line 9 in 9th line
Line 10 in 10th line
        </old>
    <new>
Line 5 in 5th line
Line 6 in 6th line
Line 7 in 7th line
Line 8 in 8th line
Line 9 in 9th line
Line 10 in 10th line
    </new>
  </edit>
</file>
</tools>



    <tools>
<terminal>
<command>
ls -l
</command>
<timeout>10000</timeout>
</terminal>
    </tools>





<tools>
<signature>
<read file="/Users/agnos/Downloads/AGNOS/Resumon/V2_1/frontend/node_modules/.vite/deps/chunk-RPCDYKBN.js" from="1000" to="2000"/>
</signature>
</tools>







<tools>
<search type="regex">
  <read path="/Users/agnos/Downloads/AGNOS/Resumon_Landing/">
    <find>(?i)head</find>
    <find>^\s*def\s+[a-zA-Z_]\w*\s*\(</find>
  </read>
</search>
</tools>




<tools>
<search type="regex">
  <read path="/Users/agnos/Downloads/AGNOS/AGEditor_2/V2/Backend/text.py">
    <find>(?i)head</find>
    <find>^\s*def\s+[a-zA-Z_]\w*\s*\(</find>
  </read>
</search>
</tools>


<tools>
<search type="grep">
  <read path="/Users/agnos/Downloads/AGNOS/AGEditor_2/V2/Backend/text.py">
    <find>(?i)head</find>
    <find>print</find>
  </read>
</search>
</tools>


