# Pilot example audit

Generated arithmetic development items. An exact checker verifies each displayed equality; no human audit has been recorded.

All traces have three equality steps. The invalid/correct variant has TWO false equalities (a corruption and a return to the correct path). It is not a one-error minimal pair. All injected errors occur at the first step: an explicit pilot confound.

## dev-01: compute `(12+7)*4-9`

Correct answer: **67**

### valid_correct

1. `(12+7)*4-9 = 19*4-9`
2. `19*4-9 = 76-9`
3. `76-9 = 67`

False equality steps: none. Proposed answer: 67.

### invalid_correct

1. `(12+7)*4-9 = 20*4-9`
2. `20*4-9 = 76-9`
3. `76-9 = 67`

False equality steps: [1, 2]. Proposed answer: 67.

### invalid_wrong

1. `(12+7)*4-9 = 20*4-9`
2. `20*4-9 = 80-9`
3. `80-9 = 71`

False equality steps: [1]. Proposed answer: 71.

## dev-02: compute `(23+8)*3-17`

Correct answer: **76**

### valid_correct

1. `(23+8)*3-17 = 31*3-17`
2. `31*3-17 = 93-17`
3. `93-17 = 76`

False equality steps: none. Proposed answer: 76.

### invalid_correct

1. `(23+8)*3-17 = 32*3-17`
2. `32*3-17 = 93-17`
3. `93-17 = 76`

False equality steps: [1, 2]. Proposed answer: 76.

### invalid_wrong

1. `(23+8)*3-17 = 32*3-17`
2. `32*3-17 = 96-17`
3. `96-17 = 79`

False equality steps: [1]. Proposed answer: 79.

## dev-03: compute `(17+26)*5-38`

Correct answer: **177**

### valid_correct

1. `(17+26)*5-38 = 43*5-38`
2. `43*5-38 = 215-38`
3. `215-38 = 177`

False equality steps: none. Proposed answer: 177.

### invalid_correct

1. `(17+26)*5-38 = 44*5-38`
2. `44*5-38 = 215-38`
3. `215-38 = 177`

False equality steps: [1, 2]. Proposed answer: 177.

### invalid_wrong

1. `(17+26)*5-38 = 44*5-38`
2. `44*5-38 = 220-38`
3. `220-38 = 182`

False equality steps: [1]. Proposed answer: 182.

## dev-04: compute `(48+19)*7-64`

Correct answer: **405**

### valid_correct

1. `(48+19)*7-64 = 67*7-64`
2. `67*7-64 = 469-64`
3. `469-64 = 405`

False equality steps: none. Proposed answer: 405.

### invalid_correct

1. `(48+19)*7-64 = 68*7-64`
2. `68*7-64 = 469-64`
3. `469-64 = 405`

False equality steps: [1, 2]. Proposed answer: 405.

### invalid_wrong

1. `(48+19)*7-64 = 68*7-64`
2. `68*7-64 = 476-64`
3. `476-64 = 412`

False equality steps: [1]. Proposed answer: 412.

## dev-05: compute `(125+37)*6-89`

Correct answer: **883**

### valid_correct

1. `(125+37)*6-89 = 162*6-89`
2. `162*6-89 = 972-89`
3. `972-89 = 883`

False equality steps: none. Proposed answer: 883.

### invalid_correct

1. `(125+37)*6-89 = 163*6-89`
2. `163*6-89 = 972-89`
3. `972-89 = 883`

False equality steps: [1, 2]. Proposed answer: 883.

### invalid_wrong

1. `(125+37)*6-89 = 163*6-89`
2. `163*6-89 = 978-89`
3. `978-89 = 889`

False equality steps: [1]. Proposed answer: 889.

## dev-06: compute `13*7+4*9`

Correct answer: **127**

### valid_correct

1. `13*7+4*9 = 91+4*9`
2. `91+4*9 = 91+36`
3. `91+36 = 127`

False equality steps: none. Proposed answer: 127.

### invalid_correct

1. `13*7+4*9 = 92+4*9`
2. `92+4*9 = 91+36`
3. `91+36 = 127`

False equality steps: [1, 2]. Proposed answer: 127.

### invalid_wrong

1. `13*7+4*9 = 92+4*9`
2. `92+4*9 = 92+36`
3. `92+36 = 128`

False equality steps: [1]. Proposed answer: 128.

## dev-07: compute `24*6+8*7`

Correct answer: **200**

### valid_correct

1. `24*6+8*7 = 144+8*7`
2. `144+8*7 = 144+56`
3. `144+56 = 200`

False equality steps: none. Proposed answer: 200.

### invalid_correct

1. `24*6+8*7 = 145+8*7`
2. `145+8*7 = 144+56`
3. `144+56 = 200`

False equality steps: [1, 2]. Proposed answer: 200.

### invalid_wrong

1. `24*6+8*7 = 145+8*7`
2. `145+8*7 = 145+56`
3. `145+56 = 201`

False equality steps: [1]. Proposed answer: 201.

## dev-08: compute `37*9+12*4`

Correct answer: **381**

### valid_correct

1. `37*9+12*4 = 333+12*4`
2. `333+12*4 = 333+48`
3. `333+48 = 381`

False equality steps: none. Proposed answer: 381.

### invalid_correct

1. `37*9+12*4 = 334+12*4`
2. `334+12*4 = 333+48`
3. `333+48 = 381`

False equality steps: [1, 2]. Proposed answer: 381.

### invalid_wrong

1. `37*9+12*4 = 334+12*4`
2. `334+12*4 = 334+48`
3. `334+48 = 382`

False equality steps: [1]. Proposed answer: 382.

## dev-09: compute `56*8+17*6`

Correct answer: **550**

### valid_correct

1. `56*8+17*6 = 448+17*6`
2. `448+17*6 = 448+102`
3. `448+102 = 550`

False equality steps: none. Proposed answer: 550.

### invalid_correct

1. `56*8+17*6 = 449+17*6`
2. `449+17*6 = 448+102`
3. `448+102 = 550`

False equality steps: [1, 2]. Proposed answer: 550.

### invalid_wrong

1. `56*8+17*6 = 449+17*6`
2. `449+17*6 = 449+102`
3. `449+102 = 551`

False equality steps: [1]. Proposed answer: 551.

## dev-10: compute `123*7+29*8`

Correct answer: **1093**

### valid_correct

1. `123*7+29*8 = 861+29*8`
2. `861+29*8 = 861+232`
3. `861+232 = 1093`

False equality steps: none. Proposed answer: 1093.

### invalid_correct

1. `123*7+29*8 = 862+29*8`
2. `862+29*8 = 861+232`
3. `861+232 = 1093`

False equality steps: [1, 2]. Proposed answer: 1093.

### invalid_wrong

1. `123*7+29*8 = 862+29*8`
2. `862+29*8 = 862+232`
3. `862+232 = 1094`

False equality steps: [1]. Proposed answer: 1094.
