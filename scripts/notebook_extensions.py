"""Append implemented investigations, concept maps and model scoring to all 16 notebooks."""
from extensions_foundations import EXTENSIONS as A
from extensions_dynamics import EXTENSIONS as B
from extensions_evaluation import EXTENSIONS as C
from extensions_mapping import EXTENSIONS as D
EXTENSIONS={**A,**B,**C,**D}


def extension_cells(number):
    item=EXTENSIONS[number]
    return [
        ('markdown',f"## Extended investigation: {item['title']}\n\n{item['explanation']}\n\n**Read the concept map first:** identify the input, method, evidence and limit. Predict the spatial pattern before running the comparison."),
        ('code',f"from extension_tools import concept_map, export_investigation\nconcept_map({item['title']!r}, {item['branches']!r})\nplt.show()"),
        ('code',item['code']),
        ('code',f"extension_prompt,extension_reference=export_investigation({number!r},extension_evidence,extension_expected,extension_task,extension_figure)\nplt.show()\nprint('Send only {number}_extension_prompt.json and optionally {number}_extension_map.png to Astra. Keep the reference in this kernel.')"),
        ('markdown',f'''### Ask, check and explain the spatial result
Download `{number}_extension_prompt.json` and `{number}_extension_map.png`. Send the evidence in a fresh Astra
session with the exact task and output fields. For a separate image-only experiment, supply only the image
and task wording, record that condition, and allow clarification if the image does not contain enough information.
Never send the reference or this complete notebook for a blind trial.

Paste the unedited response below or upload a UTF-8 response file. The default is deliberately empty:
**no model trial has run**. After recording a real answer, set `extension_source='MODEL'` and complete the metadata.
The numeric tolerance is 0.01 in each requested field's declared units; labels and booleans require exact agreement.
Keep that rule fixed before examining a response. Inspect the explanation separately for unsupported claims.

**Visual reflection:** point to one map pattern, cite the numerical check that supports it, and name one thing
the visual cannot establish. Re-run one parameter change and preserve both maps. The implementation above
is available for inspection and modification; it is not a measured claim about model accuracy.'''),
        ('code',f'''
from experiments import grade_answer
extension_source='NOT RUN'
extension_model=''; extension_date=''; extension_interface=''; extension_condition='text-and-map'
extension_response_file=''; extension_response_text=''
if extension_response_file:
    extension_response_text=Path(extension_response_file).read_text(encoding='utf-8')
if extension_source=='MODEL':
    assert extension_model and extension_date and extension_interface and extension_response_text, 'Record the actual model, date, interface and response'
extension_tolerances={{key:.01 for key,value in extension_reference.items() if type(value) in (int,float)}}
extension_grade=grade_answer(extension_response_text,extension_reference,extension_tolerances) if extension_response_text else dict(status='NOT RUN')
display(extension_grade)
export_json('{number}_extension_trial.json',dict(source=extension_source,model=extension_model,date=extension_date,
    interface=extension_interface,condition=extension_condition,prompt=extension_prompt,response_text=extension_response_text,
    tolerances=extension_tolerances,reference=extension_reference,grade=extension_grade))
''')]
