import { randomBytes, scryptSync, createCipheriv, createDecipheriv } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// Signed IPAs contain registered-device identifiers. Never upload them in plaintext.
export function seal(data, password) {
  if (!password || password.length < 32) throw Error('Use a randomly generated password of at least 32 characters');
  const salt = randomBytes(16), iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', scryptSync(password, salt, 32), iv);
  const encrypted = Buffer.concat([cipher.update(data), cipher.final()]);
  return Buffer.concat([Buffer.from('OIC1'), salt, iv, cipher.getAuthTag(), encrypted]);
}
export function unseal(data, password) {
  if (data.length < 48 || data.subarray(0, 4).toString() !== 'OIC1') throw Error('Invalid artifact');
  const decipher = createDecipheriv('aes-256-gcm', scryptSync(password, data.subarray(4, 20), 32), data.subarray(20, 32));
  decipher.setAuthTag(data.subarray(32, 48));
  return Buffer.concat([decipher.update(data.subarray(48)), decipher.final()]);
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [mode, input, output] = process.argv.slice(2);
  if (!['seal', 'unseal'].includes(mode) || !input || !output) throw Error('Usage: node scripts/seal.mjs seal|unseal input output');
  const password = process.env.ARTIFACT_PASSWORD;
  if (!password || password.length < 32) throw Error('Set ARTIFACT_PASSWORD securely (at least 32 characters)');
  writeFileSync(output, (mode === 'seal' ? seal : unseal)(readFileSync(input), password), { flag: 'wx', mode: 0o600 });
}
