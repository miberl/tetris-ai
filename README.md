# tetris-ai

<img width="388" alt="Screenshot 2021-12-01 at 23 36 28" src="https://user-images.githubusercontent.com/47005505/144331420-a985470b-41ce-45e0-b0f2-65575ecbfeb4.png">

## Specification

This version has been optimized based on rules set out by the UCL 2021 ENGF0002 challenge specification.<br />
This includes a 400-block limit and a proprietary scoring system which differs slightly from the original Nintendo NES relese.

Within this specification, it achieved the highest overall score in UCL's 2021 challenge *(52846)*.

## Artificial Intelligence 

The AI was optimised using a multi-processed genetic algorithm approach.<br />

Various population sizes and mutation rates were tried throughout this project, with mixed results. The final values have been found to be the most effective in reducing the local maxima problem.
