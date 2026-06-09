"""Flask chat UI for project generation — interactive Q&A then generates via existing pipeline."""

import os
import io
import json
import shutil
import zipfile
import threading
import tempfile
from pathlib import Path

from flask import Flask, render_template_string, request, jsonify, send_file

from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project
from coding_agent.rules_engine import build_project_rules

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Generator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; display: flex; justify-content: center; min-height: 100vh; }
  .container { max-width: 640px; width: 100%; padding: 20px; }
  h1 { text-align: center; color: #1a1a2e; margin-bottom: 24px; font-size: 24px; }
  .chat { background: #fff; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }
  .messages { padding: 20px; max-height: 480px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
  .bubble { max-width: 85%; padding: 12px 16px; border-radius: 16px; line-height: 1.5; font-size: 14px; animation: fadeIn .3s; }
  .bubble.bot { background: #e8f0fe; color: #1a1a2e; align-self: flex-start; border-bottom-left-radius: 4px; }
  .bubble.user { background: #1a73e8; color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
  .bubble.progress { background: #fef7e0; color: #5f4b00; align-self: flex-start; font-size: 13px; }
  .bubble.success { background: #e6f4ea; color: #137333; align-self: flex-start; font-size: 13px; }
  .bubble.error { background: #fce8e6; color: #c5221f; align-self: flex-start; font-size: 13px; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .input-area { border-top: 1px solid #e0e0e0; padding: 12px 16px; display: flex; gap: 8px; align-items: center; background: #fafafa; }
  .input-area input[type="text"] { flex: 1; padding: 10px 14px; border: 1px solid #d0d0d0; border-radius: 24px; font-size: 14px; outline: none; transition: border .2s; }
  .input-area input[type="text"]:focus { border-color: #1a73e8; }
  .input-area button { padding: 10px 20px; border: none; border-radius: 24px; font-size: 14px; cursor: pointer; transition: opacity .2s; background: #1a73e8; color: #fff; font-weight: 500; }
  .input-area button:hover { opacity: .85; }
  .input-area button:disabled { opacity: .4; cursor: not-allowed; }
  .input-area button.secondary { background: #e0e0e0; color: #333; }
  .btn-group { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn-group button { flex: 1; min-width: 100px; padding: 10px 16px; border: 2px solid #d0d0d0; border-radius: 12px; background: #fff; font-size: 14px; cursor: pointer; transition: all .2s; }
  .btn-group button:hover { border-color: #1a73e8; background: #e8f0fe; }
  .btn-group button.selected { border-color: #1a73e8; background: #1a73e8; color: #fff; }
  .summary { background: #f8f9fa; border-radius: 12px; padding: 16px; margin: 8px 0; font-size: 14px; line-height: 1.6; }
  .summary strong { color: #1a1a2e; }
  .generate-btn { width: 100%; padding: 14px; background: #34a853; color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: opacity .2s; }
  .generate-btn:hover { opacity: .85; }
  .generate-btn:disabled { opacity: .4; cursor: not-allowed; }
  .download-link { display: inline-block; margin-top: 12px; padding: 10px 24px; background: #1a73e8; color: #fff; text-decoration: none; border-radius: 12px; font-weight: 500; font-size: 14px; transition: opacity .2s; }
  .download-link:hover { opacity: .85; }
  .hidden { display: none; }
</style>
</head>
<body>
<div class="container">
  <h1>Project Generator</h1>
  <div class="chat">
    <div class="messages" id="messages"></div>
    <div class="input-area" id="inputArea"></div>
  </div>
  <div id="downloadArea" class="hidden" style="text-align:center;margin-top:16px;"></div>
</div>
<script>
const STEPS = [
  { key: 'idea', type: 'text', question: 'What do you want to build?' },
  { key: 'backend', type: 'choice', question: 'Which backend?', options: ['Express.js', 'FastAPI'] },
  { key: 'database', type: 'choice', question: 'Which database?', options: ['MongoDB', 'PostgreSQL'] },
  { key: 'modules', type: 'text', question: 'What entities/modules? (comma separated)' },
];

const ANSWERS = {};
let step = 0;

function addBubble(text, cls) {
  const el = document.createElement('div');
  el.className = 'bubble ' + cls;
  el.textContent = text;
  document.getElementById('messages').appendChild(el);
  el.scrollIntoView({ behavior: 'smooth' });
}

function addChoices(question, options, onSelect) {
  const area = document.getElementById('inputArea');
  area.innerHTML = '';
  const wrap = document.createElement('div');
  wrap.style.width = '100%';
  const q = document.createElement('div');
  q.textContent = question;
  q.style.cssText = 'margin-bottom:10px;font-weight:500;color:#1a1a2e;';
  wrap.appendChild(q);
  const grp = document.createElement('div');
  grp.className = 'btn-group';
  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.textContent = opt;
    btn.onclick = () => {
      grp.querySelectorAll('button').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      onSelect(opt);
    };
    grp.appendChild(btn);
  });
  wrap.appendChild(grp);
  area.appendChild(wrap);
}

function addTextInput(question, onSubmit) {
  const area = document.getElementById('inputArea');
  area.innerHTML = '';
  const inp = document.createElement('input');
  inp.type = 'text';
  inp.placeholder = question;
  inp.style.flex = '1';
  const btn = document.createElement('button');
  btn.textContent = 'Send';
  btn.onclick = () => { const v = inp.value.trim(); if (v) onSubmit(v); };
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') btn.click(); });
  area.appendChild(inp);
  area.appendChild(btn);
  inp.focus();
}

function nextStep() {
  if (step >= STEPS.length) { showSummary(); return; }
  const s = STEPS[step];
  addBubble(s.question, 'bot');
  if (s.type === 'choice') {
    addChoices(s.question, s.options, val => {
      ANSWERS[s.key] = val;
      addBubble(val, 'user');
      step++;
      nextStep();
    });
  } else {
    addTextInput(s.question, val => {
      ANSWERS[s.key] = val;
      addBubble(val, 'user');
      step++;
      nextStep();
    });
  }
}

function showSummary() {
  document.getElementById('inputArea').innerHTML = '';
  const summaryHtml = `<div class="summary">
    <strong>Project Summary</strong><br><br>
    <strong>Idea:</strong> ${ANSWERS.idea}<br>
    <strong>Backend:</strong> ${ANSWERS.backend}<br>
    <strong>Database:</strong> ${ANSWERS.database}<br>
    <strong>Auth:</strong> ${ANSWERS.auth}<br>
    <strong>Modules:</strong> ${ANSWERS.modules || '(none)'}<br>
  </div>`;
  const el = document.createElement('div');
  el.innerHTML = summaryHtml;
  document.getElementById('messages').appendChild(el.firstElementChild);
  const btn = document.createElement('button');
  btn.className = 'generate-btn';
  btn.textContent = 'Generate Project';
  btn.onclick = generateProject;
  document.getElementById('inputArea').appendChild(btn);
}

async function generateProject() {
  const btn = document.querySelector('.generate-btn');
  btn.disabled = true;
  btn.textContent = 'Generating...';
  const mods = ANSWERS.modules ? ANSWERS.modules.split(',').map(m => m.trim()).filter(Boolean) : [];
  const entities = mods.map(m => ({ name: m, fields: [], description: m }));
  const pages = mods.length ? mods.map(m => ({ name: m.charAt(0).toUpperCase() + m.slice(1), purpose: `${m} page`, entities: [m] })) : [];
  const rules = {
    project_name: ANSWERS.idea || 'Generated Project',
    project_description: ANSWERS.idea || '',
    complexity: 'intermediate',
    entities: entities,
    pages: pages,
    flow: [],
    roles: [],
    tech_stack: {
      backend: ANSWERS.backend,
      frontend: 'React',
      database: ANSWERS.database,
    },
    requirements: [],
  };
  addBubble('Generating project...', 'progress');
  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rules),
    });
    const data = await resp.json();
    if (resp.ok) {
      addBubble(`Generated ${data.files_generated} files. Packaging zip...`, 'progress');
      const zipResp = await fetch('/download');
      if (zipResp.ok) {
        const blob = await zipResp.blob();
        const url = URL.createObjectURL(blob);
        document.getElementById('downloadArea').innerHTML = `<a class="download-link" href="${url}" download="generated_project.zip">Download generated_project.zip</a>`;
        document.getElementById('downloadArea').classList.remove('hidden');
        addBubble('Project ready! Click the download link above.', 'success');
      }
    } else {
      addBubble('Error: ' + (data.error || 'Generation failed'), 'error');
      btn.disabled = false;
      btn.textContent = 'Generate Project';
    }
  } catch (e) {
    addBubble('Error: ' + e.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Generate Project';
  }
}

addBubble('Hello! I will help you generate a project. Answer a few questions:', 'bot');
nextStep();
</script>
</div>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():
    srs = request.get_json()
    if not srs:
        return jsonify({"error": "Invalid JSON body"}), 400

    from knowledge_retriever import retrieve_knowledge
    output_dir = tempfile.mkdtemp(prefix="gen_chat_")

    try:
        srs.setdefault("tech_stack", {})
        ts = srs["tech_stack"]
        ts.setdefault("frontend", "React")
        ts.setdefault("deployment", "Local")
        srs.setdefault("entities", [])
        srs.setdefault("pages", [])
        srs.setdefault("flow", [])
        srs.setdefault("roles", [])
        srs.setdefault("requirements", [])

        knowledge = retrieve_knowledge(srs)
        project_rules = build_project_rules(srs, ts)
        project_rules["knowledge"] = knowledge

        plan = generate_build_plan(project_rules)
        result = generate_project(plan, project_rules, output_dir, max_repair_attempts=0)

        app.config["LAST_OUTPUT_DIR"] = output_dir

        return jsonify({
            "files_generated": result["files_generated"],
            "all_validations_pass": result["all_validations_pass"],
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download")
def download():
    output_dir = app.config.get("LAST_OUTPUT_DIR")
    if not output_dir or not os.path.isdir(output_dir):
        return jsonify({"error": "No generated project available"}), 404

    buf = io.BytesIO()
    base = Path(output_dir)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in base.rglob("*"):
            if file_path.is_file():
                arcname = str(file_path.relative_to(base))
                zf.write(file_path, arcname)
    buf.seek(0)

    def cleanup():
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception:
            pass

    threading.Timer(60, cleanup).start()
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="generated_project.zip")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
