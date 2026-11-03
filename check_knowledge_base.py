from knowledge_base import load_knowledge_base


def main():
    documents = load_knowledge_base()

    print(f"Wczytane dokumenty: {len(documents)}")

    for document in documents:
        print(
            f"{document['id']} | "
            f"{document['category']} | "
            f"{document['title']}"
        )


if __name__ == "__main__":
    main()