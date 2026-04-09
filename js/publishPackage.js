import { execSync } from 'child_process';
import fs from 'fs';

function exec(cmd) {
  return execSync(cmd).toString();
}

function copy() {
  const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf-8'));

  delete pkg.devDependencies;
  delete pkg.scripts;

  fs.writeFileSync('./build/package.json', JSON.stringify(pkg, null, 2));

  fs.copyFileSync('README.md', './build/README.md');
}

function publishPackage() {
  copy();

  console.log(exec('npm publish --access public ./build'));
}

publishPackage();
