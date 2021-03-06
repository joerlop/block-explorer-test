import hashlib
import math
from .ecc import S256Point, Signature
from logging import getLogger

from unittest import TestCase

from .helper import (
    hash160,
    hash256,
)

LOGGER = getLogger(__name__)

# encodes num = converts num to byte format, LE.
def encode_num(num):
    if num == 0:
        return b''
    # absolute value of num.
    abs_num = abs(num)
    # negative boolean.
    negative = num < 0
    # The bytearray() method returns a bytearray object which is a mutable (can be modified) 
    # sequence of integers in the range 0 <= x < 256.
    result = bytearray()
    # loops abs_num byte by byte and appends each byte to the result.
    while abs_num:
        # appends abs_num in byte format to result.
        result.append(abs_num & 0xff)
        # shifts to the next byte.
        abs_num >>= 8
    # if the top bit is set,
    # for negative numbers we ensure that the top bit is set.
    # for positive numbers we ensure that the top bit is not set.
    # this is because when the top bit is zero, the number is positive. 
    # when it's 1, the number is negative.
    if result[-1] & 0x80: # True only if top bit is a 1
        # if top bit is already a 1, I need to add a byte to indicate it's negative or positive.
        if negative:
            result.append(0x80)
        else:
            result.append(0)
    # if top bit isn't a 1, but number is negative, then I change top bit for a 1.
    elif negative:
        # ensures that top bit is 1
        result[-1] |= 0x80
    return bytes(result)

# decodes num from byte format to int.
def decode_num(element):
    if element == b'':
        return 0
    # reverse for big endian
    big_endian = element[::-1]
    # top bit being 1 means it's negative
    if big_endian[0] & 0x80:
        negative = True
        result = big_endian[0] & 0x7f
    else:
        negative = False
        result = big_endian[0]
    for c in big_endian[1:]:
        result <<= 8
        result += c
    if negative:
        return -result
    else:
        return result

"""
The following methods (until op_16) just add encoded numbers to the stack.
"""

def op_0(stack):
    stack.append(encode_num(0))
    return True


def op_1negate(stack):
    stack.append(encode_num(-1))
    return True


def op_1(stack):
    stack.append(encode_num(1))
    return True


def op_2(stack):
    stack.append(encode_num(2))
    return True


def op_3(stack):
    stack.append(encode_num(3))
    return True


def op_4(stack):
    stack.append(encode_num(4))
    return True


def op_5(stack):
    stack.append(encode_num(5))
    return True


def op_6(stack):
    stack.append(encode_num(6))
    return True


def op_7(stack):
    stack.append(encode_num(7))
    return True


def op_8(stack):
    stack.append(encode_num(8))
    return True


def op_9(stack):
    stack.append(encode_num(9))
    return True


def op_10(stack):
    stack.append(encode_num(10))
    return True


def op_11(stack):
    stack.append(encode_num(11))
    return True


def op_12(stack):
    stack.append(encode_num(12))
    return True


def op_13(stack):
    stack.append(encode_num(13))
    return True


def op_14(stack):
    stack.append(encode_num(14))
    return True


def op_15(stack):
    stack.append(encode_num(15))
    return True


def op_16(stack):
    stack.append(encode_num(16))
    return True

# does nothing
def op_nop(stack):
    return True

# if the top stack value is not 0, the statements are executed. The top stack value is removed.
# items is a list (array) of commands that come from the script being evaluated (see evaluate method in Script class).
def op_if(stack, cmds):
    # if there's nothing in the stack, return False.
    if len(stack) < 1:
        return False
    # go through and re-make the items array based on the top stack element.
    if_cmds = [] # will hold the commands for the IF statement.
    else_cmds = [] # will hold the commands for the ELSE statement.
    current_array = if_cmds
    # boolean that indicates the if statement exited correctly.
    found = False
    # number of endifs needed to exit the if (we don't know where the if ends a priori).
    num_endifs_needed = 1
    while len(cmds) > 0:
        cmd = cmds.pop(0)
        # 99 and 100 are OP_IF and OP_NOTIF, so it would mean we have a nested loop.
        if cmd in (99, 100):
            # we increase the # of endifs needed to exit the if.
            num_endifs_needed += 1
            # add the OP_IF or OP_NOTIF to the if statement array.
            current_array.append(cmd)
        # 103 is OP_ELSE and if we only needed 1 endif, then we exit the if and get into the else statement. 
        elif num_endifs_needed == 1 and cmd == 103:
            # else statement items.
            current_array = else_cmds
        # 104 is and OP_ENDIF
        elif cmd == 104:
            # if we only needed 1 endif, exit the if statement.
            if num_endifs_needed == 1:
                found = True
                break
            else:
                # else, subtract 1 to the endifs needed to exit the if statement.
                num_endifs_needed -= 1
                # add the OP_ENDIF to the if statement array.
                current_array.append(cmd)
        # for any other operation or element, add it to the if statement array.
        else:
            current_array.append(cmd)
    # if items array is empty and we didn't exit the if statement, fail.
    if not found:
        return False
    # get the top element from the stack
    element = stack.pop()
    # if top stack element is 0, if there's an OP_ELSE, OP_ELSE statements are executed, else, 
    # nothing from the if statements gets appended back to items array to be executed.
    if decode_num(element) == 0:
        cmds[:0] = else_cmds
    # else, they are executed. All statements between the IF and the END_IF are executed, 
    # excluding statements from the OP_ELSE if there's an OP_ELSE.
    else:
        cmds[:0] = if_cmds
    return True

# duplicates the top element of the stack and pushes it to the stack.
def op_dup(stack):
    # if stack is empty, return False
    if len(stack) < 1:
        return False
    top_element = stack[-1]
    stack.append(top_element)
    return True

# consumes top element of the stack, performs a hash256 operation on it and pushes the hashed element
# into the stack.
def op_hash256(stack):
    # if stack is empty, return False
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hash256(element))
    return True

# consumes top element of the stack, performs a hash160 operation on it and pushes the hashed element
# into the stack.
def op_hash160(stack):
    # if stack is empty, return False
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hash160(element))
    return True

# consumes top 2 elements, adds them and pushes the result into the stack.
def op_add(stack):
    # if stack has less than 2 elements, return False
    if len(stack) < 2:
        return False
    element_1 = decode_num(stack.pop())
    element_2 = decode_num(stack.pop())
    elem_sum = element_1 + element_2
    stack.append(encode_num(elem_sum))
    return True

# consumes top 2 elements. pushes a 1 into the stack if the topmost 2 elements are equal. Else pushes a 0.
def op_equal(stack):
    # if stack has less than 2 elements, return False
    if len(stack) < 2:
        return False
    element_1 = stack.pop()
    element_2 = stack.pop()
    if element_1 == element_2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# op_endif logic is incorporated in the op_if function.
def op_endif(stack):
    return True

# same as op_if, but statements are executed it top value is 0.
def op_notif(stack, cmds):
    # if there's nothing in the stack, return False.
    if len(stack) < 1:
        return False
    # go through and re-make the items array based on the top stack element.
    if_cmds = [] # will hold the commands for the IF statement.
    else_cmds = [] # will hold the commands for the ELSE statement.
    current_array = if_cmds
    # boolean that indicates the if statement exited correctly.
    found = False
    # number of endifs needed to exit the if (we don't know where the if ends a priori).
    num_endifs_needed = 1
    while len(cmds) > 0:
        cmd = cmds.pop(0)
        # 99 and 100 are OP_IF and OP_NOTIF, so it would mean we have a nested loop.
        if cmd in (99, 100):
            # we increase the # of endifs needed to exit the if.
            num_endifs_needed += 1
            # add the OP_IF or OP_NOTIF to the if statement array.
            current_array.append(cmd)
        # 103 is OP_ELSE and if we only needed 1 endif, then we exit the if and get into the else statement. 
        elif num_endifs_needed == 1 and cmd == 103:
            # else statement items.
            current_array = else_cmds
        # 104 is and OP_ENDIF
        elif cmd == 104:
            # if we only needed 1 endif, exit the if statement.
            if num_endifs_needed == 1:
                found = True
                break
            else:
                # else, subtract 1 to the endifs needed to exit the if statement.
                num_endifs_needed -= 1
                # add the OP_ENDIF to the if statement array.
                current_array.append(cmd)
        # for any other operation or element, add it to the if statement array.
        else:
            current_array.append(cmd)
    # if items array is empty and we didn't exit the if statement, fail.
    if not found:
        return False
    # get the top element from the stack
    element = stack.pop()
    # if top stack element is 0, if there's an OP_ELSE, OP_ELSE statements are executed, else, 
    # nothing from the if statements gets appended back to items array to be executed.
    if decode_num(element) == 0:
        cmds[:0] = if_cmds
    # else, they are executed. All statements between the IF and the END_IF are executed, 
    # excluding statements from the OP_ELSE if there's an OP_ELSE.
    else:
        cmds[:0] = else_cmds
    return True

# Marks transaction as invalid if top stack value is not true. The top stack value is removed.
def op_verify(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        return False
    return True

# Marks transaction as invalid. 
def op_return(stack):
    return False

# Removes top element from stack and pushes it into the altstack.
def op_toaltstack(stack, altstack):
    if len(stack) < 1:
        return False
    altstack.append(stack.pop())
    return True

# Puts the input onto the top of the main stack. Removes it from the alt stack.
def op_fromaltstack(stack, altstack):
    if len(stack) < 1:
        return False
    stack.append(altstack.pop())
    return True

# Removes the top two stack items.
def op_2drop(stack):
    if len(stack) < 2:
        return False
    stack.pop()
    stack.pop()
    return True

# Duplicates the top two stack items.
def op_2dup(stack):
    if len(stack) < 2:
        return False
    elem1 = stack[-1]
    elem2 = stack[-2]
    stack.append(elem2)
    stack.append(elem1)
    return True

# Duplicates the top three stack items.
def op_3dup(stack):
    if len(stack) < 3:
        return False
    stack.extend(stack[-3:])
    return True

# Copies the pair of items two spaces back in the stack to the front.
def op_2over(stack):
    if len(stack) < 4:
        return False
    stack.extend(stack[-4:-2])
    return True

# The fifth and sixth items back are moved to the top of the stack.
def op_2rot(stack):
    if len(stack) < 6:
        return False
    stack[-6:] = stack[-4:] + stack[-6:-4]
    return True

# Swaps the top two pairs of items.
def op_2swap(stack):
    if len(stack) < 4:
        return False
    stack[-4:] = stack[-2:] + stack[-4:-2]
    return True

# If the top stack value is not 0, duplicate it.
def op_ifdup(stack):
    if len(stack) < 1:
        return False
    item = stack[-1]
    if decode_num(item) != 0:
        stack.append(item)
    return True

# Puts the number of stack items onto the stack.
def op_depth(stack):
    encoded_length = encode_num(len(stack))
    stack.append(encoded_length)
    return True

# Removes the top stack item.
def op_drop(stack):
    if len(stack) < 1:
        return False
    stack.pop()
    return True

# Removes the second-to-top stack item.
def op_nip(stack):
    if len(stack) < 2:
        return False
    stack.pop(-2)
    return True

# Copies the second-to-top stack item to the top.
def op_over(stack):
    if len(stack) < 2:
        return False
    stack.append(stack[-2])
    return True

# The item n (starting from 0) back in the stack is copied to the top. 
def op_pick(stack):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    stack.append(stack[-n-1])
    return True

# The item n back in the stack is moved to the top.
def op_roll(stack):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    stack.append(stack.pop(-n-1)) 

# The top three items on the stack are rotated to the left.
def op_rot(stack):
    if len(stack) < 3:
        return False
    stack.append(stack.pop(-3))
    return True

# The top two items on the stack are swapped.
def op_swap(stack):
    if len(stack) < 2:
        return False
    stack.append(stack.pop(-2))
    return True

# The item at the top of the stack is copied and inserted before the second-to-top item.
def op_tuck(stack):
    if len(stack) < 2:
        return False
    stack.insert(-2, stack[-1])
    return True

# Pushes the string length of the top element of the stack (without popping it).
def op_size(stack):
    if len(stack) < 1:
        return False
    stack.append(encode_num(len(stack[-1])))
    return True

# Same as OP_EQUAL, but runs OP_VERIFY afterward.
def op_equalverify(stack):
    return op_equal(stack) and op_verify(stack)

# 1 is added to the top element of the stack.
def op_1add(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    stack.append(encode_num(item + 1))
    return True

# 1 is subtracted to the top element of the stack.
def op_1sub(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    stack.append(encode_num(item - 1))
    return True

# The sign of the top element of the stack is flipped.
def op_negate(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    stack.append(encode_num(-item))
    return True

# The top element of the stack is made positive.
def op_abs(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    stack.append(encode_num(abs(item)))
    return True

# Top element is removed. If top element is 0, a 1 is pushed onto the stack, 
# otherwise a 0 is pushed onto the stack.
def op_not(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    if item == 0:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))

# Removes top element. If it is 0, a 0 is added onto the stack, otherwise a 1 is pushed onto the stack.
def op_0notequal(stack):
    if len(stack) < 1:
        return False
    item = decode_num(stack.pop())
    if item == 0:
        stack.append(encode_num(0))
    else:
        stack.append(encode_num(1))

# top element is subtracted from second-to-top stack element. Both elements are consumed. 
# result is pushed onto the stack.
def op_sub(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    result = elem2 - elem1
    stack.append(encode_num(result))
    return True

# consumes top 2 elements, if both are not 0, push 1 onto the stack. Otherwise push 0.
def op_booland(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem1 != 0 and elem2 != 0:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# consumes top 2 elements, if one of them is not 0, push 1 onto the stack. Otherwise push 0.
def op_boolor(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem1 != 0 or elem2 != 0:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# consumes top 2 elements, if they are equal, pushes a 1 onto the stack. Otherwise pushes a 0.
def op_numequal(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem1 == elem2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

def op_numequalverify(stack):
    return op_numequal(stack) and op_verify(stack)

# consumes top 2 elements, if they are not equal, pushes a 1 onto the stack. Otherwise pushes a 0.
def op_numnotequal(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem1 != elem2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top 2 elements. Pushes a 1 onto the stack if second-to-top element
# is less than top element. 0 otherwise.
def op_lessthan(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 < elem1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top 2 elements. Pushes a 1 onto the stack if second-to-top element
# is greater than top element. 0 otherwise.
def op_greaterthan(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 > elem1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top 2 elements. Pushes a 1 onto the stack if second-to-top element
# is less than or equal to top element. 0 otherwise.
def op_lessthanorequal(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 <= elem1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top 2 elements. Pushes a 1 onto the stack if second-to-top element
# is greater than or equal to the top element. 0 otherwise.
def op_greaterthanorequal(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 >= elem1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top 2 elements. Pushes the smaller element between the two onto the stack.
def op_min(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 <= elem1:
        stack.append(encode_num(elem2))
    else:
        stack.append(encode_num(elem1))
    return True

# Consumes top 2 elements. Pushes the larger element between the two onto the stack.
def op_max(stack):
    if len(stack) < 2:
        return False
    elem1 = decode_num(stack.pop())
    elem2 = decode_num(stack.pop())
    if elem2 >= elem1:
        stack.append(encode_num(elem2))
    else:
        stack.append(encode_num(elem1))
    return True

# Consumes top 3 elements. If third to top element is between second to top (min, inclusive) 
# and top elements (max, not inclusive) pushes 1 onto the stack. 0 otherwise.
def op_within(stack):
    if len(stack) < 3:
        return False
    max_elem = decode_num(stack.pop())
    min_elem = decode_num(stack.pop())
    elem = decode_num(stack.pop())
    if elem >= min_elem and elem < max_elem:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# Consumes top element of the stack, performs a ripemd160 operation on it and pushes the hashed element
# into the stack.
def op_ripemd160(stack):
    if len(stack) < 1:
        return False
    elem = stack.pop()
    stack.append(hashlib.new('ripemd160', elem).digest())
    return True

# Consumes top element of the stack, performs a sha1 operation on it and pushes the hashed element
# into the stack.
def op_sha1(stack):
    if len(stack) < 1:
        return False
    elem = stack.pop()
    stack.append(hashlib.sha1(elem).digest())
    return True

# Consumes top element of the stack, performs a sha256 operation on it and pushes the hashed element
# into the stack.
def op_sha256(stack):
    if len(stack) < 1:
        return False
    elem = stack.pop()
    # hashlib.new method receives as its parameter a bytes-like object and returns a SHA256 Hash Object.
    # digest() converts the SHA256 object into bytes format.
    stack.append(hashlib.sha256(elem).digest())
    return True

# Same as OP_CHECKSIG, but OP_VERIFY is executed afterward.
def op_checksigverify(stack, z):
    return op_checksig(stack, z) and op_verify(stack)

# consumes 2 stack elements (pubkey and signature) and determines if they are valid for this transaction. 
# OP_CHECKSIG will push a 1 to the stack if they are valid. 0 otherwise - page 112
def op_checksig(stack, z):
    # if stack is has less than 2 elements, fail.
    if len(stack) < 2:
        return False
    # sec_pubkey is the top element of stack.
    sec_pubkey = stack.pop()
    # take off the last byte of the signature as that's the hash_type.
    # Signature format is [<DER signature> <1 byte hash-type>]. Hashtype value is last byte of the sig.
    der_signature = stack.pop()[:-1]
    try:
        point = S256Point.parse(sec_pubkey)
        sig = Signature.parse(der_signature)
    except (ValueError, SyntaxError) as e:
        LOGGER.info(e)
        return False
    valid = point.verify(z, sig)
    # push a 1 if it's valid, 0 otherwise.
    if valid:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True

# If all signatures are valid, 1 is returned, 0 otherwise. 
# Due to a bug, one extra unused value is removed from the stack - page 148.
# REWRITE: one sig can only sign one pubkey. Then that pubkey should be removed from consideration.
def op_checkmultisig(stack, z): 
    if len(stack) < 1:
        return False
    # n is the number of public keys
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    # get all the public keys into a list.
    pubkeys = []
    for _ in range(n):
        pubkeys.append(stack.pop())
    if len(stack) < 1:
        return False
    # m is the number of signatures
    m = decode_num(stack.pop())
    # m + 2 because of the additional element at the bottom of the stack that is added.
    if len(stack) < m + 1:
        return False
    # get all the signatures.
    signatures = []
    for _ in range(m):
        # take off last byte, which is the hashtype
        signatures.append(stack.pop()[:-1])
    if len(stack) < 1:
        return False
    # we remove the last element from the stack (the one included because the off by one error)
    stack.pop()
    # verify all the signatures against all pubkeys. If a signature isn't valid for any pubkeys, fail.
    try:
        sigs = [Signature.parse(signature) for signature in signatures]
        points = [S256Point.parse(pubkey) for pubkey in pubkeys]
    except (ValueError, SyntaxError) as e:
        LOGGER.info(e)
        return False
    # variable to count the number of valid signatures.
    count = 0
    # in the next loop, we check that each signature is valid for a pubkey.
    while len(points) > 0:
        # point is popped so each signature can only be valid for 1 point.
        point = points.pop()
        for sig in sigs:
            # if the signature is valid for this pubkey, increase the count and break from the while
            # to check next signature.
            if point.verify(z, sig):
                count += 1
    # if the number of valid signatures is m = each signature is valid for some pubkey, then script is valid.
    if count == m:
        stack.append(encode_num(1))
    # else, script should fail.
    else:
        stack.append(encode_num(0))
    return True

# Same as OP_CHECKMULTISIG, but OP_VERIFY is executed afterward.
def op_checkmultisigverify(stack, z):
    return op_checkmultisig(stack, z) and op_verify(stack)   
        

class TestOp(TestCase):

    def test_op_2over(self):
        stack = [1, 2, 3, 4]
        op_2over(stack)
        self.assertEqual(stack, [1, 2, 3, 4, 1, 2])
    
    def test_op_2rot(self):
        stack = [1, 2, 3, 4, 5, 6]
        op_2rot(stack)
        self.assertEqual(stack, [3, 4, 5, 6, 1, 2])
    
    def test_op_2swap(self):
        stack = [1, 2, 3, 4]
        op_2swap(stack)
        self.assertEqual(stack, [3, 4, 1, 2])
    
    def test_op_depth(self):
        stack = [1, 2, 3, 4]
        op_depth(stack)
        self.assertEqual(stack, [1, 2, 3, 4, encode_num(4)])
    
    def test_op_drop(self):
        stack = [1, 2]
        op_drop(stack)
        self.assertEqual(stack, [1])
    
    def test_op_nip(self):
        stack = [1, 2, 3]
        op_nip(stack)
        self.assertEqual(stack, [1, 3])
    
    def test_op_over(self):
        stack = [1, 2, 3]
        op_over(stack)
        self.assertEqual(stack, [1, 2, 3, 2])
    
    def test_op_pick(self):
        stack = [1, 2, 3, 4, encode_num(3)]
        op_pick(stack)
        self.assertEqual(stack, [1, 2, 3, 4, 1])
    
    def test_op_roll(self):
        stack = [1, 2, 3, 4, encode_num(3)]
        op_roll(stack)
        self.assertEqual(stack, [2, 3, 4, 1])
    
    def test_op_rot(self):
        stack = [1, 2, 3]
        op_rot(stack)
        self.assertEqual(stack, [2, 3, 1])

    def test_op_swap(self):
        stack = [1, 2, 3]
        op_swap(stack)
        self.assertEqual(stack, [1, 3, 2])
    
    def test_op_tuck(self):
        stack = [1, 2]
        op_tuck(stack)
        self.assertEqual(stack, [2, 1, 2])
    
    # def test_op_size(self):
    #     stack = [encode_num(16)]
    #     op_size(stack)
    #     self.assertEqual(stack, [encode_num(16), encode_num(2)])
    
    def test_op_equalverify(self):
        stack = [1, 1]
        self.assertEqual(op_equalverify(stack), True)
    
    def test_op_1add(self):
        stack = [encode_num(10)]
        op_1add(stack)
        self.assertEqual(stack, [encode_num(11)])
    
    def test_op_1sub(self):
        stack = [encode_num(10)]
        op_1sub(stack)
        self.assertEqual(stack, [encode_num(9)])

    def test_op_negate(self):
        stack = [encode_num(-10)]
        op_negate(stack)
        self.assertEqual(stack, [encode_num(10)])

        stack = [encode_num(10)]
        op_negate(stack)
        self.assertEqual(stack, [encode_num(-10)])
    
    def test_op_abs(self):
        stack = [encode_num(-10)]
        op_abs(stack)
        self.assertEqual(stack, [encode_num(10)])

        stack = [encode_num(10)]
        op_abs(stack)
        self.assertEqual(stack, [encode_num(10)])
    
    def test_op_not(self):
        stack = [encode_num(0)]
        op_not(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(2)]
        op_not(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_0notequal(self):
        stack = [encode_num(0)]
        op_0notequal(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(10)]
        op_0notequal(stack)
        self.assertEqual(stack, [encode_num(1)])

    def test_op_sub(self):
        stack = [encode_num(10), encode_num(4)]
        op_sub(stack)
        self.assertEqual(stack, [encode_num(6)])
    
    def test_op_booland(self):
        stack = [encode_num(1), encode_num(25)]
        op_booland(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(0), encode_num(25)]
        op_booland(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_boolor(self):
        stack = [encode_num(1), encode_num(25)]
        op_boolor(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(0), encode_num(25)]
        op_boolor(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(0), encode_num(0)]
        op_boolor(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_numequal(self):
        stack = [encode_num(10), encode_num(10)]
        op_numequal(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(9), encode_num(10)]
        op_numequal(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_numnotequal(self):
        stack = [encode_num(10), encode_num(10)]
        op_numnotequal(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(9), encode_num(10)]
        op_numnotequal(stack)
        self.assertEqual(stack, [encode_num(1)])
    
    def test_op_lessthan(self):
        stack = [encode_num(1), encode_num(2)]
        op_lessthan(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(2), encode_num(2)]
        op_lessthan(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(10), encode_num(2)]
        op_lessthan(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_greaterthan(self):
        stack = [encode_num(1), encode_num(2)]
        op_greaterthan(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(2), encode_num(2)]
        op_greaterthan(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(10), encode_num(2)]
        op_greaterthan(stack)
        self.assertEqual(stack, [encode_num(1)])

    def test_op_lessthanorequal(self):
        stack = [encode_num(1), encode_num(2)]
        op_lessthanorequal(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(2), encode_num(2)]
        op_lessthanorequal(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(10), encode_num(2)]
        op_lessthanorequal(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_greaterthanorequal(self):
        stack = [encode_num(1), encode_num(2)]
        op_greaterthanorequal(stack)
        self.assertEqual(stack, [encode_num(0)])

        stack = [encode_num(2), encode_num(2)]
        op_greaterthanorequal(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(10), encode_num(2)]
        op_greaterthanorequal(stack)
        self.assertEqual(stack, [encode_num(1)])
    
    def test_op_min(self):
        stack = [encode_num(10), encode_num(100)]
        op_min(stack)
        self.assertEqual(stack, [encode_num(10)])
    
    def test_op_max(self):
        stack = [encode_num(10), encode_num(100)]
        op_max(stack)
        self.assertEqual(stack, [encode_num(100)])
    
    def test_op_within(self):
        stack = [encode_num(5), encode_num(2), encode_num(10)]
        op_within(stack)
        self.assertEqual(stack, [encode_num(1)])

        stack = [encode_num(5), encode_num(2), encode_num(5)]
        op_within(stack)
        self.assertEqual(stack, [encode_num(0)])
    
    def test_op_ripemd160(self):
        stack = [encode_num(1)]
        op_ripemd160(stack)
        self.assertEqual(stack, [hashlib.new('ripemd160', encode_num(1)).digest()])
    
    def test_op_sha1(self):
        stack = [encode_num(1)]
        op_sha1(stack)
        self.assertEqual(stack, [hashlib.new('sha1', encode_num(1)).digest()])
    
    def test_op_sha256(self):
        stack = [encode_num(1)]
        op_sha256(stack)
        self.assertEqual(stack, [hashlib.new('sha256', encode_num(1)).digest()])
    
    def test_op_checksig(self):
        z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
        sec = bytes.fromhex('04887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34')
        sig = bytes.fromhex('3045022000eff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c022100c7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab601')
        stack = [sig, sec]
        self.assertTrue(op_checksig(stack, z))
        self.assertEqual(decode_num(stack[0]), 1)

    def test_op_checksigverify(self):
        z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
        sec = bytes.fromhex('04887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34')
        sig = bytes.fromhex('3045022000eff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c022100c7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab601')
        stack = [sig, sec]
        self.assertTrue(op_checksigverify(stack, z))
    
    def test_op_checkmultisig(self):
        z = 0xe71bfa115715d6fd33796948126f40a8cdd39f187e4afb03896795189fe1423c
        sig1 = bytes.fromhex('3045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701')
        sig2 = bytes.fromhex('3045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201')
        sec1 = bytes.fromhex('022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb70')
        sec2 = bytes.fromhex('03b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb71')
        stack = [b'', sig1, sig2, b'\x02', sec1, sec2, b'\x02']
        self.assertTrue(op_checkmultisig(stack, z))
        self.assertEqual(decode_num(stack[0]), 1)


OP_CODE_FUNCTIONS = {
    0: op_0,
    79: op_1negate,
    81: op_1,
    82: op_2,
    83: op_3,
    84: op_4,
    85: op_5,
    86: op_6,
    87: op_7,
    88: op_8,
    89: op_9,
    90: op_10,
    91: op_11,
    92: op_12,
    93: op_13,
    94: op_14,
    95: op_15,
    96: op_16,
    97: op_nop,
    99: op_if,
    100: op_notif,
    105: op_verify,
    106: op_return,
    107: op_toaltstack,
    108: op_fromaltstack,
    109: op_2drop,
    110: op_2dup,
    111: op_3dup,
    112: op_2over,
    113: op_2rot,
    114: op_2swap,
    115: op_ifdup,
    116: op_depth,
    117: op_drop,
    118: op_dup,
    119: op_nip,
    120: op_over,
    121: op_pick,
    122: op_roll,
    123: op_rot,
    124: op_swap,
    125: op_tuck,
    130: op_size,
    135: op_equal,
    136: op_equalverify,
    139: op_1add,
    140: op_1sub,
    143: op_negate,
    144: op_abs,
    145: op_not,
    146: op_0notequal,
    147: op_add,
    148: op_sub,
    154: op_booland,
    155: op_boolor,
    156: op_numequal,
    157: op_numequalverify,
    158: op_numnotequal,
    159: op_lessthan,
    160: op_greaterthan,
    161: op_lessthanorequal,
    162: op_greaterthanorequal,
    163: op_min,
    164: op_max,
    165: op_within,
    166: op_ripemd160,
    167: op_sha1,
    168: op_sha256,
    169: op_hash160,
    170: op_hash256,
    172: op_checksig,
    173: op_checksigverify,
    174: op_checkmultisig,
    175: op_checkmultisigverify,
    176: op_nop,
    # 177: op_checklocktimeverify,
    # 178: op_checksequenceverify,
    179: op_nop,
    180: op_nop,
    181: op_nop,
    182: op_nop,
    183: op_nop,
    184: op_nop,
    185: op_nop,
}

OP_CODE_NAMES = {
    0: 'OP_0',
    76: 'OP_PUSHDATA1',
    77: 'OP_PUSHDATA2',
    78: 'OP_PUSHDATA4',
    79: 'OP_1NEGATE',
    81: 'OP_1',
    82: 'OP_2',
    83: 'OP_3',
    84: 'OP_4',
    85: 'OP_5',
    86: 'OP_6',
    87: 'OP_7',
    88: 'OP_8',
    89: 'OP_9',
    90: 'OP_10',
    91: 'OP_11',
    92: 'OP_12',
    93: 'OP_13',
    94: 'OP_14',
    95: 'OP_15',
    96: 'OP_16',
    97: 'OP_NOP',
    99: 'OP_IF',
    100: 'OP_NOTIF',
    103: 'OP_ELSE',
    104: 'OP_ENDIF',
    105: 'OP_VERIFY',
    106: 'OP_RETURN',
    107: 'OP_TOALTSTACK',
    108: 'OP_FROMALTSTACK',
    109: 'OP_2DROP',
    110: 'OP_2DUP',
    111: 'OP_3DUP',
    112: 'OP_2OVER',
    113: 'OP_2ROT',
    114: 'OP_2SWAP',
    115: 'OP_IFDUP',
    116: 'OP_DEPTH',
    117: 'OP_DROP',
    118: 'OP_DUP',
    119: 'OP_NIP',
    120: 'OP_OVER',
    121: 'OP_PICK',
    122: 'OP_ROLL',
    123: 'OP_ROT',
    124: 'OP_SWAP',
    125: 'OP_TUCK',
    130: 'OP_SIZE',
    135: 'OP_EQUAL',
    136: 'OP_EQUALVERIFY',
    139: 'OP_1ADD',
    140: 'OP_1SUB',
    143: 'OP_NEGATE',
    144: 'OP_ABS',
    145: 'OP_NOT',
    146: 'OP_0NOTEQUAL',
    147: 'OP_ADD',
    148: 'OP_SUB',
    154: 'OP_BOOLAND',
    155: 'OP_BOOLOR',
    156: 'OP_NUMEQUAL',
    157: 'OP_NUMEQUALVERIFY',
    158: 'OP_NUMNOTEQUAL',
    159: 'OP_LESSTHAN',
    160: 'OP_GREATERTHAN',
    161: 'OP_LESSTHANOREQUAL',
    162: 'OP_GREATERTHANOREQUAL',
    163: 'OP_MIN',
    164: 'OP_MAX',
    165: 'OP_WITHIN',
    166: 'OP_RIPEMD160',
    167: 'OP_SHA1',
    168: 'OP_SHA256',
    169: 'OP_HASH160',
    170: 'OP_HASH256',
    171: 'OP_CODESEPARATOR',
    172: 'OP_CHECKSIG',
    173: 'OP_CHECKSIGVERIFY',
    174: 'OP_CHECKMULTISIG',
    175: 'OP_CHECKMULTISIGVERIFY',
    176: 'OP_NOP1',
    177: 'OP_CHECKLOCKTIMEVERIFY',
    178: 'OP_CHECKSEQUENCEVERIFY',
    179: 'OP_NOP4',
    180: 'OP_NOP5',
    181: 'OP_NOP6',
    182: 'OP_NOP7',
    183: 'OP_NOP8',
    184: 'OP_NOP9',
    185: 'OP_NOP10',
}