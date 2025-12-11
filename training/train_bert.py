import os, pandas as pd, numpy as np, torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'model_save')
BERT_NAME = 'bert-base-uncased'
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 2
LR = 2e-5
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class NewsDS(Dataset):
    def __init__(self, texts, labels, tok):
        self.texts = texts
        self.labels = labels
        self.tok = tok
    def __len__(self): return len(self.texts)
    def __getitem__(self, i):
        enc = self.tok(
            str(self.texts[i]),
            truncation=True, padding='max_length', max_length=MAX_LEN,
            return_tensors='pt'
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item['labels'] = torch.tensor(int(self.labels[i]), dtype=torch.long)
        return item

def load_data():
    path_fake = os.path.join(DATA_DIR, 'Fake.csv')
    path_true = os.path.join(DATA_DIR, 'True.csv')

    print("📄 Loading:", path_fake)
    print("📄 Loading:", path_true)

    # ✅ Use correct encoding
    fake = pd.read_csv(path_fake, encoding="utf-8", engine="python", on_bad_lines='skip')
    true = pd.read_csv(path_true, encoding="utf-8", engine="python", on_bad_lines='skip')

    fake['label'] = 0
    true['label'] = 1

    # ✅ Ensure cols present
    if 'title' not in fake.columns:
        fake['title'] = ""
    if 'title' not in true.columns:
        true['title'] = ""

    if 'text' not in fake.columns:
        if 'content' in fake.columns:
            fake['text'] = fake['content']
        else:
            raise ValueError("Fake.csv missing both 'text' and 'content'!")

    if 'text' not in true.columns:
        if 'content' in true.columns:
            true['text'] = true['content']
        else:
            raise ValueError("True.csv missing both 'text' and 'content'!")

    df = pd.concat(
        [fake[['title', 'text', 'label']], true[['title', 'text', 'label']]],
        ignore_index=True
    )

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df['text_full'] = (
        df['title'].fillna('') + ' [SEP] ' + df['text'].fillna('')
    ).str.slice(0, 2000)

    X_train, X_val, y_train, y_val = train_test_split(
        df['text_full'], df['label'],
        test_size=0.1, random_state=42, stratify=df['label']
    )
    return X_train.tolist(), X_val.tolist(), y_train.tolist(), y_val.tolist()

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    tokenizer = BertTokenizer.from_pretrained(BERT_NAME)
    model = BertForSequenceClassification.from_pretrained(BERT_NAME, num_labels=2)
    model.to(DEVICE)

    X_tr, X_val, y_tr, y_val = load_data()
    train_ds = NewsDS(X_tr, y_tr, tokenizer)
    val_ds   = NewsDS(X_val, y_val, tokenizer)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl   = DataLoader(val_ds, batch_size=BATCH_SIZE)

    optim = AdamW(model.parameters(), lr=LR)
    total_steps = len(train_dl) * EPOCHS
    sched = get_linear_schedule_with_warmup(optim, num_warmup_steps=0, num_training_steps=total_steps)
    ce = torch.nn.CrossEntropyLoss()

    for epoch in range(EPOCHS):
        model.train()
        tot = 0
        for batch in train_dl:
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            out = model(**batch)
            loss = out.loss
            loss.backward()
            optim.step()
            sched.step()
            optim.zero_grad()
            tot += loss.item()
        print(f"Epoch {epoch+1}/{EPOCHS} - train loss: {tot/len(train_dl):.4f}")

        # quick val
        model.eval()
        correct, count = 0, 0
        with torch.no_grad():
            for batch in val_dl:
                labels = batch['labels'].to(DEVICE)
                batch = {k: v.to(DEVICE) for k, v in batch.items()}
                logits = model(**batch).logits
                pred = torch.argmax(logits, dim=1)
                correct += (pred == labels).sum().item()
                count += labels.size(0)
        print(f"Val acc: {correct/count:.4f}")

    # save fine-tuned model & tokenizer
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print("✅ Saved fine-tuned model to", MODEL_DIR)

if __name__ == "__main__":
    train()
