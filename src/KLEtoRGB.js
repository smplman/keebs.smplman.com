import testData from './tests/keyboard-layout.json';

const X_COORD_OFFSET = 0.0
const Y_COORD_OFFSET = 0.0

export function KLEtoRGB (data, options) {
  // data = testData;

  let keys = [];

  // for each row
  let currentY = -0.5;
  let keyNum = 0;

  data.forEach((row, y) => {  
    // for each key
    let currentX = -0.5;
    let keyWidth = 1;
    let keyHeight = 1;

    row.forEach((key, x) => {
      // This configures the size of the key in the next key
      if (typeof key === 'object') {
        if (key.x) {
          currentX += key.x;
        }
        if (key.y) {
          currentY += key.y
        }
        if (key.w) {
          keyWidth = key.w
        }
        if (key.h) {
          keyHeight = key.h
        }
      } else if (typeof key === 'string') {
        const newKey = {
          num: keyNum,
          xUnit: currentX + keyWidth / 2,
          yUnit: currentY + keyHeight / 2,
          legend: key,
          width: keyWidth,
          height: keyHeight
        }

        keys.push(newKey);

        currentX += keyWidth;
        keyNum += 1;
        // reset key size for next key
        keyWidth = 1;
        keyHeight = 1;
      } else {
        console.error(`invalid key in json row ${y} col ${x}`);
        return;
      }
    });
    currentY += 1.0;
    currentX = 0;
  });

  keys.forEach((key) => {
    key.xCoord = parseFloat(key.xUnit * 19.05 + X_COORD_OFFSET).toFixed(8);
    key.yCoord = parseFloat(key.yUnit * 19.05 + Y_COORD_OFFSET).toFixed(8);
  });

  // find min/max of x and y
  const minX = Math.min.apply(Math, keys.map((k) => { return k.xCoord; }));
  const minY = Math.min.apply(Math, keys.map((k) => { return k.yCoord; }));

  // math to normalise to top left 0,0
  keys.forEach((key) => {
    key.xCoord -= minX;
    key.yCoord -= minY;
  });

  const maxX = Math.max.apply(Math, keys.map((k) => { return k.xCoord; })) - minX;
  const maxY = Math.max.apply(Math, keys.map((k) => { return k.yCoord; })) - minY;

  // console.log(`minX:${minX}, minY:${minY}, maxX:${maxX}, maxY:${maxY}`);

  keys.forEach((key) => {
    key.modX = Math.round(key.xCoord * 224 / maxX);
    key.modY = Math.round(key.yCoord *64 / maxY);
  });

  // center keyboard over middle
  const midX = maxX / 2;
  const midY = maxY / 2;

  // console.log('min', minX, minY);
  // console.log('mid', midX, midY);
  // console.log('max', maxX, maxY);

  keys.forEach((key) => {
    key.xcoordm = +((key.xCoord - midX) / midX).toFixed(10);
    key.ycoordm = +((key.yCoord - midY) / midY).toFixed(10);

    let atan2Angle = Math.atan2(key.xcoordm, key.ycoordm);
    if (atan2Angle < 0) {
      atan2Angle += Math.PI * 2;
    }
    atan2Angle /= 2 * Math.PI;
    key.atan2 = atan2Angle;

    key.distance = Math.sqrt(key.xcoordm**2 + key.ycoordm**2);

    key.angle = Math.round(key.atan2 * 256);

    const dist = Math.round(key.distance * 256);
    key.distFinal = dist > 255 ? 255 : dist;
  });

  // console.log(keys);

  // list of indexes/letter starts. e.g. [A,B] or [A,B,C,D,E,F]
  let listOfLetters = [];
  keys.forEach((key) => {
    const letter = key.legend.charAt(0);
    if (!listOfLetters.includes(letter) && isNaN(letter)) {
      listOfLetters.push(letter);
    }
  });

  console.log('letters:', listOfLetters);

  // build output
  const xyCoords = buildCoordString(keys, options, {x: 'modX', y: 'modY'}).slice(0, -1);
  const angleCoords = buildCoordString(keys, options, {x: 'angle', y: 'distFinal'}).slice(0, -1);
  let str = '';
  str += '// XY COORDS \n';
  str += xyCoords;
  str += '\n\n\n';
  str += '// ANGLE DIST COORDS \n';
  str += angleCoords;

  return str;
}

function buildCoordString (keys, options, coords) {
  // list for unused so we can generate which ones to disable
  let listUnused = [];

  console.log('COORDS PRINTING');

  // build output
  let outputString = '';
  // counter because row sucks and wont let us start at our index start
  let count = options.indexStart;
  // row counter
  let rowCounter = 0;
  // prev index letter
  let prevIDLetter = keys[0].legend.charAt(0);

  keys.forEach((key) => {
    const IDLetter = key.legend.charAt(0);
    const IDNumber = key.legend.substring(1);

    // console.log(ID, IDLetter, IDNumber, prevIDLetter);

    // check if we moved to another bank e.g. A->B
    if (IDLetter != prevIDLetter) {
      console.log('moved to another bank')
      // if we're at the end, but are missing from count to index_end
      // then fill them in as blank
      // e.g. index_end = 64, current ID = A60, next ID = B02
      // fill in A61 - A64
      if (count != options.indexEnd + 1) {
        while (count <= options.indexEnd) {
          listUnused.push(IDLetter + count);
            outputString += '{255,255}, ';
            rowCounter += 1;
            if (rowCounter == options.numPerLine) {
                outputString += '\n';
                rowCounter = 0;
            }
            count += 1;
        }
      }
      count = options.indexStart;
      prevIDLetter = IDLetter
    }

    if (count != IDNumber) {
      // check for missing gaps of LEDs
      // e.g. A1 -> A5, missing A2, A3, A4
      // this will fill in A2 - A4
      while (count < IDNumber) {
        listUnused.push(IDLetter + count);
        outputString += '{255,255}, ';
        rowCounter += 1;
        if (rowCounter == options.numPerLine) {
          outputString += '\n';
          rowCounter = 0;
        }
        count += 1
      }
    }

    outputString += `{${key[coords.x].toString().padEnd(3)},${key[coords.y].toString().padStart(3)}}, `;
    // new line at <num_per_line>
    rowCounter += 1;
    if (rowCounter == options.numPerLine) {
      outputString += '\n';
      rowCounter = 0;
    }
    count += 1;
  });

  console.log('UNUSED:', listUnused);

  return outputString;
}