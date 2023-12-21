import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import SMOTE

def retrain_classifier(df):
    X = df['author_and_message']
    y = df['encoded'].tolist()

    # Count Vectorise
    vectorizer = CountVectorizer()
    X_counts = vectorizer.fit_transform(X)

    # TFIDF Convert
    tfidf_transformer = TfidfTransformer()
    X_tfidf = tfidf_transformer.fit_transform(X_counts)

    smote = SMOTE(random_state=42, k_neighbors=4)

    X_train, y_train = smote.fit_resample(X_tfidf, y)

    dt_classifier = DecisionTreeClassifier(
        class_weight='balanced',
        splitter='random',
        max_features='sqrt'  
    )
    dt_classifier.fit(X_train, y_train)

    return vectorizer, tfidf_transformer, dt_classifier

def update_encoder(df):
    # Encoding the emoji column to numeric values
    df['encoded'] = pd.factorize(df['reply_emojis'])[0]

    emojis = pd.factorize(df['reply_emojis'])[1]

    # creating a function to get the emoji back from the numbers. 
    encoded_to_string = {i: string for i, string in enumerate(emojis)}
    return encoded_to_string

def filter_df(df):
    """
    Filter out rows from the DataFrame where the emoji reaction is used less than 5 times.

    Args:
    df (pd.DataFrame): A DataFrame with columns 'author', 'original_message', 'reply_emojis', and 'encoded'.

    Returns:
    pd.DataFrame: A DataFrame filtered based on the emoji reaction count.
    """
    df['author_and_message'] = df['author'] + ' ' + df['original_message']

    # Count the occurrences of each emoji
    emoji_counts = df['reply_emojis'].value_counts()

    # Filter to keep only rows where the emoji reaction count is 5 or more
    filtered_df = df[df['reply_emojis'].map(emoji_counts) >= 5]

    return filtered_df

def retrain_bot():
    df = pd.read_csv('training.csv')

    df = filter_df(df)

    encoded_to_string = update_encoder(df)
    vectorizer, tfidf_transformer, classifier = retrain_classifier(df)

    return vectorizer, tfidf_transformer, classifier, encoded_to_string
