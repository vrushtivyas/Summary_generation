import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from transformers import BartForConditionalGeneration, BartTokenizer
import spacy
from docx import Document

# Load pre-trained BART model and tokenizer
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def identify_topics(text):
    doc = nlp(text)
    topics = set()
    for ent in doc.ents:
        topics.add(ent.text)
    return ", ".join(topics)

def highlight_key_points(text, key_points):
    highlighted_text = text
    for point in key_points:
        highlighted_text = highlighted_text.replace(point, f"{point}")
    return highlighted_text

def generate_summary(style="concise"):
    if not input_text.get("1.0", tk.END).strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return

    # Disable the button and show loading status
    generate_button.config(state=tk.DISABLED)
    status_label.config(text="Generating summary... Please wait.")
    window.update_idletasks()

    try:
        text = input_text.get("1.0", tk.END).strip()

        # Adjust prompt and generation settings based on the chosen style
        if style == "concise":
            prompt = "Generate a concise summary: " + text
            max_len = 80
            temperature = 1.0
            repetition_penalty = 2.5
        elif style == "detailed":
            prompt = "Generate a detailed summary: " + text
            max_len = 200
            temperature = 0.7
            repetition_penalty = 1.5
        elif style == "domain-specific":
            prompt = "Generate a summary focusing on key insights: " + text
            max_len = 120
            temperature = 0.8
            repetition_penalty = 2.0
        else:
            raise ValueError("Invalid summary style selected.")

        # Tokenize and encode the prompt
        inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        # Generate summary with adjusted parameters
        summary_ids = model.generate(
            inputs,
            max_length=max_len,
            min_length=30,
            length_penalty=2.0,
            num_beams=4,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            early_stopping=True
        )
        
        # Decode the summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Identify and highlight key points
        topics = identify_topics(text)
        highlighted_summary = highlight_key_points(summary, topics.split(", "))

        # Update the output text
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, highlighted_summary)

    except Exception as e:
        print(f"Error during summarization: {e}")
        messagebox.showerror("Error", f"Failed to generate summary: {e}")
    
    # Enable the button and update the status
    generate_button.config(state=tk.NORMAL)
    status_label.config(text="Summary generated successfully!")

def save_summary():
    summary = output_text.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showwarning("Save Error", "No summary to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(summary)
        messagebox.showinfo("Saved", f"Summary saved to {file_path}")

def export_summary():
    summary = output_text.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showwarning("Export Error", "No summary to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word documents", "*.docx")])
    if file_path:
        doc = Document()
        doc.add_paragraph(summary)
        doc.save(file_path)
        messagebox.showinfo("Exported", f"Summary exported to {file_path}")

def save_feedback():
    feedback = feedback_text.get("1.0", tk.END).strip()
    if not feedback:
        messagebox.showwarning("Feedback Error", "No feedback to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(feedback)
        messagebox.showinfo("Saved", f"Feedback saved to {file_path}")

def reset_fields():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    feedback_text.delete("1.0", tk.END)
    status_label.config(text="Ready to generate summary.")

# Setting up the main window
window = tk.Tk()
window.title("AI-Powered Newsletter Summarizer")
window.geometry("600x800")
window.configure(bg="#f0f4f7")  # Light background color for a professional look

# Title label
title_label = tk.Label(window, text="AI-Powered Newsletter Summarizer", bg="#f0f4f7", fg="#34495e", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Input label
input_label = tk.Label(window, text="Enter the newsletter text below:", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
input_label.pack(anchor="w", padx=20, pady=5)

# Input text box (ScrolledText)
input_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=10, font=("Arial", 11), bg="#ffffff", fg="#2c3e50", bd=2, relief="groove")
input_text.pack(padx=20, pady=10)

# Summary length selection
length_label = tk.Label(window, text="Select summary length:", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
length_label.pack(anchor="w", padx=20, pady=5)

summary_length = tk.IntVar(value=150)  # Default summary length

length_short = tk.Radiobutton(window, text="Short (50 characters)", variable=summary_length, value=50, bg="#f0f4f7", fg="#34495e", font=("Arial", 11))
length_medium = tk.Radiobutton(window, text="Medium (150 characters)", variable=summary_length, value=150, bg="#f0f4f7", fg="#34495e", font=("Arial", 11))
length_long = tk.Radiobutton(window, text="Long (300 characters)", variable=summary_length, value=300, bg="#f0f4f7", fg="#34495e", font=("Arial", 11))

length_short.pack(anchor="w", padx=20)
length_medium.pack(anchor="w", padx=20)
length_long.pack(anchor="w", padx=20)

# Summary style selection
style_label = tk.Label(window, text="Select summary style:", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
style_label.pack(anchor="w", padx=20, pady=5)

summary_style = tk.StringVar(value="concise")

style_concise = tk.Radiobutton(window, text="Concise", variable=summary_style, value="concise", bg="#f0f4f7", fg="#34495e", font=("Arial", 11))
style_detailed = tk.Radiobutton(window, text="Detailed", variable=summary_style, value="detailed", bg="#f0f4f7", fg="#34495e", font=("Arial", 11))
style_domain_specific = tk.Radiobutton(window, text="Domain-Specific", variable=summary_style, value="domain-specific", bg="#f0f4f7", fg="#34495e", font=("Arial", 11))

style_concise.pack(anchor="w", padx=20)

# Continue the code for UI elements setup
style_detailed.pack(anchor="w", padx=20)
style_domain_specific.pack(anchor="w", padx=20)

# Generate button
generate_button = tk.Button(window, text="Generate Summary", command=lambda: generate_summary(summary_style.get()), bg="#3498db", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
generate_button.pack(pady=10)

# Status label for feedback
status_label = tk.Label(window, text="Ready to generate summary.", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
status_label.pack(pady=5)

# Output label
output_label = tk.Label(window, text="Generated Summary:", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
output_label.pack(anchor="w", padx=20, pady=5)

# Output text box (ScrolledText)
output_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=8, font=("Arial", 11), bg="#ecf0f1", fg="#2c3e50", bd=2, relief="groove")
output_text.pack(padx=20, pady=10)

# Save button
save_button = tk.Button(window, text="Save Summary", command=save_summary, bg="#2ecc71", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
save_button.pack(pady=5)

# Export button
export_button = tk.Button(window, text="Export Summary", command=export_summary, bg="#3498db", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
export_button.pack(pady=5)

# Share button
share_button = tk.Button(window, text="Share Summary", command=lambda: messagebox.showinfo("Share Feature", "Share functionality is not implemented."), bg="#e67e22", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
share_button.pack(pady=5)

# Feedback section
feedback_label = tk.Label(window, text="Provide your feedback:", bg="#f0f4f7", fg="#34495e", font=("Arial", 12))
feedback_label.pack(anchor="w", padx=20, pady=5)

feedback_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=6, font=("Arial", 11), bg="#ffffff", fg="#2c3e50", bd=2, relief="groove")
feedback_text.pack(padx=20, pady=10)

feedback_button = tk.Button(window, text="Submit Feedback", command=save_feedback, bg="#9b59b6", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
feedback_button.pack(pady=5)

# Reset button
reset_button = tk.Button(window, text="Reset", command=reset_fields, bg="#e74c3c", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat")
reset_button.pack(pady=5)

# Run the application
window.mainloop()