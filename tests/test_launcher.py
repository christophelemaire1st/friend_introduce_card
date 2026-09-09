import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = next(ROOT.glob('友達*'))
SPEC = importlib.util.spec_from_file_location('launcher', BASE / 'Word配置.py')
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def test_filename(self):
        self.assertEqual(launcher.output_name('久保田学園　A<>:"/\\|?*教室. '),
                         '友達紹介カード_A_________教室.docx')

    def test_selection(self):
        with tempfile.TemporaryDirectory(prefix='日本語 space ') as tmp:
            base = Path(tmp)
            with self.assertRaises(ValueError):
                launcher.select_source(None, base)
            first = base / '古い_編集済み.html'
            first.touch()
            os.utime(first, (1, 1))
            newest = base / '新しい_編集済み.html'
            newest.touch()
            self.assertEqual(launcher.select_source(None, base), newest)
            self.assertEqual(launcher.select_source(str(first)), first.resolve())

    @unittest.skipUnless(os.environ.get('RUN_EXPORT_TESTS'), 'requires installed export dependencies')
    def test_export_and_reject_missing_images(self):
        template = next(BASE.glob('*.html')).read_text(encoding='utf-8')
        out = BASE / launcher.output_name('自動テスト教室')
        self.assertFalse(out.exists())
        with tempfile.TemporaryDirectory(prefix='日本語 space ') as tmp:
            source = Path(tmp) / 'テスト_編集済み.html'
            script = '''<script>
            document.querySelector('#schoolFront').textContent='久保田学園　自動テスト教室';
            document.querySelector('#schoolBack').textContent='久保田学園　自動テスト教室';
            const canvas=document.createElement('canvas'); canvas.width=100; canvas.height=100;
            const ctx=canvas.getContext('2d');ctx.fillStyle='blue';ctx.fillRect(0,0,100,100);
            for(const id of ['photo','qrDetails','qr']) document.getElementById(id).src=canvas.toDataURL();
            </script>'''
            source.write_text(template.replace('</body>', script+'</body>'), encoding='utf-8')
            cmd = [sys.executable, str(BASE / 'Word配置.py'), str(source)]
            try:
                result = subprocess.run(cmd, cwd=tmp, capture_output=True, env=dict(os.environ, PYTHONUTF8='1'))
                self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8')+result.stderr.decode('utf-8'))
                original = out.read_bytes()
                with zipfile.ZipFile(out) as doc:
                    xml = ET.fromstring(doc.read('word/document.xml'))
                    ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                          'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
                    self.assertEqual(len(xml.findall('.//w:tbl', ns)), 2)
                    self.assertEqual(len(xml.findall('.//wp:anchor', ns)), 20)
                    for extent in xml.findall('.//wp:extent', ns):
                        self.assertEqual((extent.get('cx'), extent.get('cy')), ('3276000', '1980000'))
                source.write_text(template, encoding='utf-8')
                result = subprocess.run(cmd, cwd=tmp, capture_output=True, env=dict(os.environ, PYTHONUTF8='1'))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('未設定', result.stderr.decode('utf-8'))
                self.assertEqual(out.read_bytes(), original)
            finally:
                out.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
