import gradio as gr
from .funcs import (gr_health_check,
                    gr_clear_rag, 
                    gr_load_files, 
                    gr_inference,
                    gr_get_vector_dbs, 
                    gr_query_rag, 
                    gr_create_rag)

# Inference
input_prompt = gr.Textbox(label='Prompt', show_copy_button=True)
input_root_prompt = gr.Textbox(value='', label='Root Prompt', lines=4, show_copy_button=True)
input_file_attachments = gr.File(label='Attachments', file_types=['text', '.csv','.json', '.pdf'], file_count='multiple')
input_vector_dbs = gr.Dropdown(choices=[], multiselect=True, label='Vector DBs', info='Bases de datos vectoriales a consultar.', interactive=True)
input_rag_mode = gr.Dropdown(choices=['Directo', 'Agente'], value='Directo', multiselect=False, label='RAG Mode', info='Modo de consultar al RAG.', interactive=True)
output_response = gr.Textbox(label='Response', show_copy_button=True)
output_context = gr.Textbox(label='Context', scale=1, show_copy_button=True, lines=20, max_lines=20, autoscroll=False)

# RAG
rag_input_query = gr.Textbox(label='Query', show_copy_button=True, lines=5)
rag_input_vector_db = gr.Dropdown(choices=[], multiselect=False, label='Vector DB', info='Seleccione una DB para consultarla o cargarla.', interactive=True)
rag_input_vector_db_id = gr.Textbox(label='vector_db_id', info='Nombre de la DB', lines=1, max_lines=1)
rag_input_chunk_size_in_tokens = gr.Number(value=128, label='chunk_size_in_tokens')
rag_output_response = gr.Textbox(label='Response', show_copy_button=True, lines=20, max_lines=20, autoscroll=False)
rag_file = gr.File(label='Load Files', file_types=['text', '.csv','.json', '.pdf'], file_count='multiple')
rag_folder = gr.File(label='Load Folder', file_count='directory')
rag_button_load = gr.Button('Load')
rag_button_clear = gr.Button('Clear RAG')
rag_button_create = gr.Button('Create')
rag_output_create = gr.Markdown(value='.', container=True)
rag_output_load = gr.Markdown(label='Output', value='.', container=True, show_label=True)


def update_vector_dbs() -> dict[str, any]:
    vector_dbs = gr_get_vector_dbs()
    return gr.update(choices=vector_dbs, value=None)

with gr.Blocks() as demo:

    with gr.Tab('Inferencia'):
        gr.Markdown('## **Utiliza la Inferencia sola o con RAG.** ##')
        with gr.Row():
            with gr.Column():
                input_prompt.render()
                input_root_prompt.render()
                with gr.Row():
                    input_vector_dbs.render()
                    with gr.Column():
                        gr.Button(value="Actualizar DBs").click(fn=update_vector_dbs, outputs=[input_vector_dbs,])
                        input_rag_mode.render()
                    

                gr.Button(value="Inferir", variant='primary').click(
                    fn=gr_inference,
                    inputs=[input_prompt, input_root_prompt, input_vector_dbs, input_rag_mode],
                    outputs=[output_response, output_context]
                )

            with gr.Column():
                output_response.render()
                output_context.render()

    with gr.Tab('RAG'):
        gr.Markdown('## **Consulta el RAG, carga archivos y crea nuevas DB Vectoriales.** ##')
        with gr.Row():
            with gr.Column():
                gr.Markdown('### **Seleccion de DB** ###')
                rag_input_vector_db.render()
                gr.Button(value="Actualizar DBs").click(fn=update_vector_dbs, outputs=[rag_input_vector_db,])
            with gr.Column():
                gr.Markdown('### **Creacion de DB** ###')
                rag_input_vector_db_id.render()
                rag_button_create.render()
                rag_button_create.click(
                    fn=gr_create_rag,
                    inputs=[rag_input_vector_db_id,],
                    outputs=[rag_output_create,]
                )
        with gr.Row():
            rag_output_create.render()
        with gr.Row():
            with gr.Column():
                rag_input_query.render()

                gr.Button(value="Consultar", variant='primary').click(
                    fn=gr_query_rag,
                    inputs=[rag_input_query, rag_input_vector_db],
                    outputs=[rag_output_response]
                )

                gr.Markdown(value='### **Carga archivos al RAG** ###')
                with gr.Row():
                    rag_file.render()
                    rag_folder.render()
                rag_input_chunk_size_in_tokens.render()
                with gr.Row():
                    rag_button_clear.render()
                    rag_button_load.render()
                rag_output_load.render()

                rag_button_load.click(
                    fn=gr_load_files,
                    inputs=[rag_file, rag_folder, rag_input_vector_db, rag_input_chunk_size_in_tokens],
                    outputs=[rag_output_load]
                )

                rag_button_clear.click(
                    fn=gr_clear_rag,
                    inputs=[rag_input_vector_db],
                    outputs=[rag_output_load]
                )
            
            with gr.Column():
                rag_output_response.render()

    # Footer #
    with gr.Row():
        gr.Markdown(value=gr_health_check, every=20, container=True)

        

if __name__ == "__main__":
    demo.launch()
