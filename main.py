from drafter import *
set_website_title("SteganoCleats")
set_website_framed(False)

from bakery import assert_equal
from PIL import Image as PIL_Image
from dataclasses import dataclass
set_site_information(
    author="lillilub@udel.edu",
    description="""
    SteganoCleats is a web application that lets users hide secret messages inside soccer cleat images.
    It uses steganography by storing data in the green channel of PNG files, changing only the least
    significant bits so the image looks the same to the human eye. A three digit header is added to
    record the message length, and the site provides tools to encode new messages, decode hidden ones,
    and save them in a personal locker. The project combines soccer culture with computer science to
    make learning about steganography fun and interactive.
    """,
    sources=[
        "https://drafter-edu.github.io/drafter/contents.html"
    ],
    planning=["Design.pdf"],
    links=["https://github.com/UD-F25-CS1/cs1-website-f25-lillilub", "https://www.youtube.com/watch?v=gKw0me_xYZU"]
)

@dataclass
class State:
    image: PIL_Image
    decoded_message: str
    encode_message: str
    message_to_encode: str
    cleat_record: list[str]
    soccer_clicks: int

def even_or_odd_bit(num:int) -> str:
    """
        Purpose: Determines wheter the int is even or odd and returns a bit like stirng that corresponds
        Arg: num (int) - a whole number
        Returns: str - '1' if n is odd and '0' if n is even
    """
    if num % 2 != 0:
        return '1'
    else:
        return '0'
assert_equal(even_or_odd_bit(0), '0')
assert_equal(even_or_odd_bit(243), '1')

def decode_single_char(color_values: list[int]) -> str:
    """
    Purpose: Decode list of 8 colors intensity numbers and then convert them into a single ASCII character.
    Args: color_values (list[int]): 8 ints reperesenting color intensities
    Returns: str: a single ASCII character that was decoded from the binary string, returns empty string if there is not 8 values.
    """
    if len(color_values) != 8:
        return ""

    binary = ""
    for number in color_values:
        binary += even_or_odd_bit(number)

    return chr(int(binary, 2))

assert_equal(decode_single_char([43,54,56]), '')
assert_equal(decode_single_char([43,43,43,43,43]), '')

def decode_chars(color_values: list[int], num_chars: int) -> str:
    """
    Purpose: Converts color values into a string of characters
    Args:
        color_values (list[int]) - are intenstiy values
        num_chars (int) - # of characters to decode
    Returns:
        str - decoded characters
        None - if input length is wrong
    """

    if len(color_values) != num_chars*8:
        return None

    result = ""
    for character_number in range(num_chars):
        start = character_number * 8
        end = start + 8
        group = color_values[start:end]
        result = result + decode_single_char(group)

    return result
assert_equal(decode_chars([46, 47, 46, 46, 47, 44, 46, 44], 1), "H")
assert_equal(decode_chars([0,3,3], 1), None)

def get_message_length(color_values: list[int], header_chars: int) -> int:
    """
    Purpose:
        Gets the number of characters in the hidden message from the header
    Args:
        color_values (list[int]) - intensity values
        header_chars (int) - # of characters in the header
    Returns:
        int - # of characters in the hidden message
        0 - if the input is not valid or the header isnt a int
    """
    if len(color_values) < header_chars * 8:
        return 0

    length = header_chars * 8
    header_values = color_values[:length]
    header_text = decode_chars(header_values, header_chars)

    if header_text.isdigit():
        return int(header_text)
    return 0

assert_equal(get_message_length([20, 254, 45, 95, 40, 90, 20, 40, 200, 254, 45,
                                95, 40, 95, 20, 45,220, 250, 45, 95, 48, 95, 24, 44], 3), 54)
assert_equal(get_message_length([],2), 0)

def get_color_values(image: PIL_Image, channel_index: int) -> list[int]:
    """
    Purpose: Get color intensity values from one channel of an image into column-major order
    Args:
        image (PIL_Image) - the image to read from
        channel_index (int) - 0 for red, 1 for green, 2 for blue
    Returns:
        list[int] - intensity values from selected channel

    Cannot be unit tested, unless upload specific file
    """
    width, length = image.size
    result = []
    for x in range(width):
        for y in range(length):
            pixel = image.getpixel((x,y))
            result.append(pixel[channel_index])
    return result

def get_encoded_message(color_values: list[int]) -> str:
    """
    Purpose:
        Decodes hidden messages from the color intensity values

    Args:
        color_values (list[int]) - all the intensity values including the header and message

    Returns:
        str - the decoded hiddden message and "" - if the message length isnt good or invalid
    """
    header_chars = 3
    header_values = color_values[0: header_chars * 8]
    message_length = get_message_length(header_values, header_chars)

    if message_length == 0:
        return ""

    start = header_chars * 8
    end = start + message_length * 8
    message_values = color_values[start:end]
    return decode_chars(message_values, message_length)

assert_equal(get_encoded_message([254, 254, 255, 255, 254, 254, 254, 254]), " ")
assert_equal(get_encoded_message([254]), " ")

def prepend_header(message: str) -> str:
    """
    Purpose: takes in a message and and returns a string
    Args: message (str) - the message you are puttingg in
    Returns: str with same string and a message length
    """
    length = len(message)
    lengh_header = 3 - len(str(length))
    header = ("0" * lengh_header) + str(length)
    return header + message

assert_equal(prepend_header("hi"),"002hi")
assert_equal(prepend_header("i"),"001i")

def message_to_binary(message: str) -> str:
    """
    Purpose: converts a messsage from a strinng to binary
    Args: messages (str) - the message you are putting in
    returns: str - string of binary
    """
    binary_string = ""
    for char in message:
        ascii_value = ord(char)
        binary_char = format(ascii_value, '08b')
        binary_string += binary_char
    return binary_string

assert_equal(message_to_binary("Hi"), "0100100001101001")
assert_equal(message_to_binary("058"),"001100000011010100111000")


def new_color_value(original_value: int, bit: str) -> int:
    """
    purpose: orginial color intensity value to hide a single bit
    args: original_value (int) and bit (str)
    returns: int of the single bit
    """
    if bit == '1':
        if original_value %2 == 0:
            return original_value + 1
        else:
            return original_value
    elif bit == '0':
        if original_value % 2 != 0:
            return original_value - 1
        else:
            return original_value
    else:
        return 0
    assert_equal(new_color_value(100, '1'), 101)
    assert_equal(new_color_value(100, '0'), 100)

def hide_bits(picture: PIL_Image.Image, bits: str) -> PIL_Image.Image:
    """
    Purpose: Hide a binary string inside the green channel
    Args:
        picture (PIL_Image.Image): The image to encode into.
        bits (str): Binary string containing the message to hide.
    Returns:
        PIL_Image.Image: A copy of the image with the hidden bits encoded.
    Cannot be Unit Tested
    """
    width, height = picture.size
    bit_idx = 0
    total_bits = len(bits)

    new_picture = picture.copy()

    if new_picture.mode != 'RGB':
        new_picture = new_picture.convert('RGB')

    for x in range(width):
        for y in range(height):
            if bit_idx < total_bits:
                pixel = new_picture.getpixel((x, y))
                r = pixel[0]
                g = pixel[1]
                b = pixel[2]
                bit = bits[bit_idx]
                g = new_color_value(g, bit)

                new_picture.putpixel((x, y), (r, g, b))
                bit_idx += 1
    return new_picture

@route
def soccer_click(state: State) -> Page:
    """soccer click counter ON home page."""
    state.soccer_clicks += 1
    return index(state)

@route
def index(state: State) -> Page:
    """The home page of StengoCleats. Provides buttons to the 4 main parts"""
    return Page(state, [
        "Welcome to StengoCleats",
        "A place where you can hide messages in soccer cleats",
        "for soccer fans only",
        "Soccer Clicks: " + str(state.soccer_clicks),
        Button("Tap for Extra Credit", soccer_click),
        Button("Encode", encode),
        Button("Decode", decode),
        Button("Locker", locker),
        Button("About", about)
    ])

@route
def encode(state: State) -> Page:
    """The encode page, where you can upload a image and add a message"""
    return Page(state, [
        "Encode Message",
        "For soccer cleat options, click the link below and download one of the six cleat PNGs:",
        Link("Cleat Options on GitHub", "https://github.com/UD-F25-CS1/cs1-website-f25-lillilub"),
        TextArea("message_to_encode","enter your message you want to hide here (delete this text)"),
        FileUpload("image", accept="image/png"),
        Button("Encode", encode_process),
        Button("Home", index)
    ])

@route
def encode_process(state: State, message_to_encode: str, image: PIL_Image.Image) -> Page:
    """the page that encodes your file into a image with the message hidden inside"""
    full_message = prepend_header(message_to_encode)
    binary_data = message_to_binary(full_message)
    encoded_image = hide_bits(image, binary_data)
    state.image = encoded_image
    state.encode_message = message_to_encode

    return Page(state, [
        "Encode Message",
        "Your Message was encode into the cleats, right click and save file as png!",
        Image(encoded_image,500,500),
        Button("Encode Another", encode),
        Button("Home", index)
    ])

@route
def decode(state: State) -> Page:
    """page that decodes a file you uploaded if it has a secret message"""

    return Page(state, [
        "Decode Message",
        FileUpload("image", accept="image/png"),
        Button("Decode", decode_process),
        Button("Home", index)
    ])


@route
def decode_process(state: State, image: PIL_Image.Image = None) -> Page:
    """the decoder function that gets the message from the png you uploaded"""

    color_values = get_color_values(image, 1)
    decoded = get_encoded_message(color_values)
    state.decoded_message = decoded
    state.cleat_record.append(decoded)

    return Page(state, [
        "Decode Message",
        "Hidden message: " + decoded,
        Button("Decode Another", decode),
        Button("View Locker", locker),
        Button("Home", index)
    ])

@route
def locker(state: State) -> Page:
    """the locker that saves your encoded and decoded messages"""
    text = [
        "Message Locker",
        "Saved messages:"
    ]
    for message in state.cleat_record:
        text.append(message)

    text.append(Button("Home", index))

    return Page(state, text)

@route
def about(state: State) -> Page:
    """about page that teachs the viewers about my website and the process"""
    return Page(state, [
        "About SteganoCleats",
        "I Like soccer so I hid my data in soccer cleats png images"
        "Steganography is the practice of hiding data within other data.",
        "Here is how it works:",
        "- Messages are hidden in the green channel of PNG images",
        "- Each bit is stored in the least significant bit of a pixel",
        "- Even pixels = 0 bit, Odd pixels = 1 bit",
        "- A 3-character numeric header stores the message length",
        "- The image looks identical to the human eye",
        Button("Home", index)
    ])

set_website_style("mvp")
add_website_css("""
body {
    background-color: lightblue;
    font-size: 20px;}
""")


assert_equal(
 locker(State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0)),
 Page(state=State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0),
      content=['Message Locker', 'Saved messages:', Button(text='Home', url='/')]))

assert_equal(
    encode(State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0)),
    Page(
        state=State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0),
        content=[
            'Encode Message',
            'For soccer cleat options, click the link below and download one of the six cleat PNGs:',
            Link(text='Cleat Options on GitHub', url='https://github.com/UD-F25-CS1/cs1-website-f25-lillilub'),
            TextArea(name='message_to_encode', default_value='enter your message you want to hide here (delete this text)'),
            FileUpload(name='image'),
            Button('Encode', '/encode_process'),
            Button('Home', '/')
        ]
    )
)

assert_equal(
 decode(State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0)),
 Page(state=State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0),
      content=['Decode Message',
               FileUpload(name='image'),
               Button(text='Decode', url='/decode_process'),
               Button(text='Home', url='/')]))

assert_equal(
 index(State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0)),
 Page(state=State(image=None, decoded_message='', encode_message='', message_to_encode='', cleat_record=[], soccer_clicks=0),
      content=['Welcome to StengoCleats',
               'A place where you can hide messages in soccer cleats',
               'for soccer fans only',
               'Soccer Clicks: 0',
               Button(text='Tap for Extra Credit', url='/soccer_click'),
               Button(text='Encode', url='/encode'),
               Button(text='Decode', url='/decode'),
               Button(text='Locker', url='/locker'),
               Button(text='About' , url='/about')]))
hide_debug_information()
start_server(State(None, "", "", "", [], 0))




