# Loads data for both books and movies, returning a dictionary with two keys, 'books' and 'movies', one for
# each subset of the collection.
def load_collections():
    # Load the two collections.
    book_collection, max_book_id = load_collection("books.csv")
    movie_collection, max_movie_id = load_collection("movies.csv")

    # Check for error.
    if book_collection is None or movie_collection is None:
        return None, None

    # Return the composite dictionary.
    return {"books": book_collection, "movies": movie_collection}, max(max_book_id, max_movie_id)


# Loads a single collection and returns the data as a dictionary.  Upon error, None is returned.
def load_collection(file_name):
    max_id = -1
    try:
        # Create an empty collection.
        collection = {}

        # Open the file and read the field names
        collection_file = open(file_name, "r")
        field_names = collection_file.readline().rstrip().split(",")

        # Read the remaining lines, splitting on commas, and creating dictionaries (one for each item)
        for item in collection_file:
            field_values = item.rstrip().split(",")
            collection_item = {}
            for index in range(len(field_values)):
                if (field_names[index] == "Available") or (field_names[index] == "Copies") or (field_names[index] == "ID"):
                    collection_item[field_names[index]] = int(field_values[index])
                else:
                    collection_item[field_names[index]] = field_values[index]
            # Add the full item to the collection.
            collection[collection_item["ID"]] = collection_item
            # Update the max ID value
            max_id = max(max_id, collection_item["ID"])

        # Close the file now that we are done reading all of the lines.
        collection_file.close()

    # Catch IO Errors, with the File Not Found error the primary possible problem to detect.
    except FileNotFoundError:
        print("File not found when attempting to read", file_name)
        return None
    except IOError:
        print("Error in data file when reading", file_name)
        return None

    # Return the collection.
    return collection, max_id


# Display the menu of commands and get user's selection.  Returns a string with  the user's reauexted command.
# No validation is performed.
def prompt_user_with_menu():
    print("\n\n********** Welcome to the Collection Manager. **********")
    print("COMMAND    FUNCTION")
    print("  ci         Check in an item")
    print("  co         Check out an item")
    print("  ab         Add a new book")
    print("  am         Add a new movie")
    print("  db         Display books")
    print("  dm         Display movies")
    print("  qb         Query for books")
    print("  qm         Query for movies")
    print("  x          Exit")
    return input("Please enter a command to proceed: ")


# Print one item in the same order as the sample output.
def print_item(item):
    print("ID:", item["ID"])

    # All of the other fields were already loaded in their original order.
    for field in item:
        if field != "ID":
            print(field + ":", item[field])
    print()


# Search the collection using part of a title, author, publisher, director, or genre.
def query_collection(collection):
    query = input("Enter a query string to use for the search: ").lower()

    # The outer dictionary uses IDs as keys, so each ID gets us an item.
    for item_id in collection:
        item = collection[item_id]

        # Books and movies have different fields to check.
        if "Author" in item:
            if (query in item["Title"].lower() or
                    query in item["Author"].lower() or
                    query in item["Publisher"].lower()):
                print_item(item)
        else:
            if (query in item["Title"].lower() or
                    query in item["Director"].lower() or
                    query in item["Genre"].lower()):
                print_item(item)


# Find an item using its ID, whether it is a book or movie.
def find_item(library_collections, action):
    response = input("Enter the ID for the item you wish to check " + action + ": ")

    # Make sure the user entered a number before converting it to an integer.
    if not response.isdigit():
        return None

    item_id = int(response)

    if item_id in library_collections["books"]:
        return library_collections["books"][item_id]
    elif item_id in library_collections["movies"]:
        return library_collections["movies"][item_id]
    else:
        return None


# Check in a copy if one has actually been checked out.
def check_in(library_collections):
    item = find_item(library_collections, "in")

    if item is None:
        print("That ID does not match an item in the collection.")
    elif item["Available"] < item["Copies"]:
        item["Available"] += 1
        print("Your check in has succeeded.")
        print_item(item)
    else:
        print("All copies are already available, so this item can not be checked in.")


# Check out a copy only when there is one available.
def check_out(library_collections):
    item = find_item(library_collections, "out")

    if item is None:
        print("That ID does not match an item in the collection.")
    elif item["Available"] > 0:
        item["Available"] -= 1
        print("Your check out has succeeded.")
        print_item(item)
    else:
        print("No copies of the item are available for check out.")


# Display the collection 10 items at a time.
def display_collection(collection):
    count = 0

    for item_id in collection:
        print_item(collection[item_id])
        count += 1

        # Pause every ten items unless there are no more items to show.
        if count % 10 == 0 and count < len(collection):
            answer = input("Press enter to show more items, or type 'm' to return to the menu: ")
            if answer.lower() == "m":
                return


# Get whole numbers for pages, years, and the number of copies.
def get_number(question):
    response = input(question)

    # Keep asking until the value can be converted without an error.
    while not response.isdigit():
        print("Please enter a whole number.")
        response = input(question)

    return int(response)


# Ask for the information needed to add a new book.
def add_book(book_collection, max_existing_id):
    print("Please enter the following attributes for the new book.")

    book = {}
    book["Title"] = input("Title: ")
    book["Author"] = input("Author: ")
    book["Publisher"] = input("Publisher: ")
    book["Pages"] = str(get_number("Pages: "))
    book["Year"] = str(get_number("Year: "))
    book["Copies"] = get_number("Copies: ")
    book["Available"] = book["Copies"]

    # Let the user review the information before adding the book.
    print("You have entered the following data:")
    for field in book:
        print(field + ":", book[field])
    print()

    answer = input("Press enter to add this item to the collection.  Enter 'x' to cancel.")
    if answer.lower() != "x":
        # Use the largest existing ID plus one so there are no duplicates.
        max_existing_id += 1
        book["ID"] = max_existing_id
        book_collection[max_existing_id] = book

    return max_existing_id


# Add a new movie using the same process as adding a book.
def add_movie(movie_collection, max_existing_id):
    print("Please enter the following attributes for the new movie.")

    movie = {}
    movie["Title"] = input("Title: ")
    movie["Director"] = input("Director: ")
    movie["Length"] = input("Length: ")
    movie["Genre"] = input("Genre: ")
    movie["Year"] = str(get_number("Year: "))
    movie["Copies"] = get_number("Copies: ")
    movie["Available"] = movie["Copies"]

    # Show the information first in case the user wants to cancel.
    print("You have entered the following data:")
    for field in movie:
        print(field + ":", movie[field])
    print()

    answer = input("Press enter to add this item to the collection.  Enter 'x' to cancel.")
    if answer.lower() != "x":
        max_existing_id += 1
        movie["ID"] = max_existing_id
        movie_collection[max_existing_id] = movie

    return max_existing_id


# This is the main program function.  It runs the main loop which prompts the user and performs the requested actions.
def main():
    # Load the collections, and check for an error.
    library_collections, max_existing_id = load_collections()

    if library_collections is None:
        print("The collections could not be loaded. Exiting.")
        return

    # No error, so print out a success message with the number of items.
    total_item_count = len(library_collections['books']) + len(library_collections['movies'])
    print(f"The collections have loaded successfully with {total_item_count} items. ")

    # Display the error and get the operation code entered by the user.  We perform this continuously until the
    # user enters "x" to exit the program.  Calls the appropriate function that corresponds to the requested operation.
    operation = prompt_user_with_menu()
    while operation != "x":
        ###############################################################################################################
        ###############################################################################################################
        # HINTS HINTS HINTS!!! READ THE FOLLOWING SECTION OF COMMENTS!
        ###############################################################################################################
        ###############################################################################################################
        #
        # The commented-out code below gives you a some good hints about how to structure your code.
        #
        # FOR BASIC REQUIREMENTS:
        #
        # Notice that each operation is supported by a function.  That is good design, and you should use this approach.
        # Moreover, you will want to define even MORE functions to help break down these top-level user operations into
        # even smaller chunks that are easier to code.
        #
        # FOR ADVANCED REQUIREMENTS:
        #
        # Notice the "max_existing_id" variable?  When adding a new book or movie to the collection, you'll need to
        # assign the new item a unique ID number.  This variable is included to make that easier for you to achieve.
        # Remember, if you assign a new ID to a new item, be sure to keep "max_existing_id" up to date!
        #
        # Have questions? Ask on Piazza!
        #
        ###############################################################################################################
        ###############################################################################################################
        if operation == "ci":
            check_in(library_collections)
        elif operation == "co":
            check_out(library_collections)
        elif operation == "ab":
            max_existing_id = add_book(library_collections["books"], max_existing_id)
        elif operation == "am":
            max_existing_id = add_movie(library_collections["movies"], max_existing_id)
        elif operation == "db":
            display_collection(library_collections["books"])
        elif operation == "dm":
            display_collection(library_collections["movies"])
        elif operation == "qb":
            query_collection(library_collections["books"])
        elif operation == "qm":
            query_collection(library_collections["movies"])
        else:
            print("Unknown command.  Please try again.")

        operation = prompt_user_with_menu()


# Kick off the execution of the program.
main()
# ChatGPT helped me write the logic for searching and displaying the collection, specifically looping through the dictrionaries, and also helped me develop the check-in and out system and assigning unique ID's to new entries.