import os

file_path = r'C:\Users\THIN 15\Desktop\SNEAKO_PROJECT\sneako_project\templates\adminpanel\order_detail.html'

content = """{% extends 'adminpanel/admin_index.html' %}
{% load static %}

{% block title %}Order #{{ order.id }} Details | SNEAKO Admin{% endblock %}
{% block active_orders %}active{% endblock %}
{% block page_title %}Order Details #{{ order.id }}{% endblock %}

{% block content %}
<div class="row g-4">
    <div class="col-lg-8">
        <div class="admin-card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Order Items</h5>
                <span class="status-badge {{ order.status|lower|slugify }}">{{ order.status }}</span>
            </div>
            <div class="table-responsive">
                <table class="table table-borderless align-middle">
                    <thead class="bg-light">
                        <tr class="small text-muted text-uppercase">
                            <th class="ps-4">Product</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th class="pe-4 text-end">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in order.items.all %}
                        <tr>
                            <td class="ps-4">
                                <div class="d-flex align-items-center gap-3">
                                    <div class="bg-light rounded-3"
                                        style="width: 50px; height: 50px; overflow: hidden;">
                                        {% if item.product.image %}
                                        <img src="{{ item.product.image.url }}" class="w-100 h-100 object-fit-contain">
                                        {% else %}
                                        <div class="w-100 h-100 d-flex align-items-center justify-content-center">
                                            <i data-lucide="package" class="text-muted"></i>
                                        </div>
                                        {% endif %}
                                    </div>
                                    <div>
                                        <div class="fw-bold">{{ item.product_name }}</div>
                                        <div class="text-muted small">SKU: {{ item.product.sku|default:"N/A" }}</div>
                                    </div>
                                </div>
                            </td>
                            <td>₹{{ item.price }}</td>
                            <td>{{ item.quantity }}</td>
                            <td class="pe-4 text-end fw-bold">₹{{ item.price|add:0|mul:item.quantity|default:item.price
                                }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="row g-4">
            <div class="col-md-6">
                <div class="admin-card h-100">
                    <div class="card-header">
                        <h5 class="mb-0">Customer Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="text-muted small d-block">Full Name</label>
                            <div class="fw-bold">{{ order.address.full_name }}</div>
                        </div>
                        <div class="mb-3">
                            <label class="text-muted small d-block">Email Address</label>
                            <div class="fw-bold">{{ order.user.email }}</div>
                        </div>
                        <div class="mb-0">
                            <label class="text-muted small d-block">Phone Number</label>
                            <div class="fw-bold">{{ order.address.phone }}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="admin-card h-100">
                    <div class="card-header">
                        <h5 class="mb-0">Shipping Address</h5>
                    </div>
                    <div class="card-body text-dark">
                        {{ order.address.street_address }}<br>
                        {{ order.address.city }}, {{ order.address.state }} {{ order.address.zip_code }}<br>
                        {{ order.address.country }}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <!-- Status Update Form -->
        <div class="admin-card mb-4 border-primary border-top border-4">
            <div class="card-header">
                <h5 class="mb-0">Manage Order</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label fw-bold">Order Status</label>
                        <select name="status" class="form-select rounded-pill">
                            {% for code, label in order.STATUS_CHOICES %}
                            <option value="{{ code }}" {% if order.status == code %}selected{% endif %}>{{ label }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">Payment Status</label>
                        <select name="payment_status" class="form-select rounded-pill">
                            {% for code, label in order.PAYMENT_STATUS_CHOICES %}
                            <option value="{{ code }}" {% if order.payment_status == code %}selected{% endif %}>{{ label
                                }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn btn-dark w-100 rounded-pill py-2">Update Order</button>
                </form>
            </div>
        </div>

        <!-- Order Summary -->
        <div class="admin-card">
            <div class="card-header">
                <h5 class="mb-0">Order Summary</h5>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Subtotal</span>
                    <span>₹{{ order.subtotal }}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Shipping</span>
                    <span>₹{{ order.shipping_cost }}</span>
                </div>
                {% if order.discount_amount > 0 %}
                <div class="d-flex justify-content-between mb-2 text-danger">
                    <span>Discount ({{ order.coupon.code|default:"COUPON" }})</span>
                    <span>-₹{{ order.discount_amount }}</span>
                </div>
                {% endif %}
                <div class="d-flex justify-content-between mb-3 border-bottom pb-2">
                    <span class="text-muted">Tax</span>
                    <span>₹{{ order.tax }}</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span class="fw-bold fs-5">Total</span>
                    <span class="fw-bold fs-5 text-primary">₹{{ order.total_amount }}</span>
                </div>
                <div class="mt-4 p-3 bg-light rounded-3 d-flex align-items-center justify-content-between">
                    <div class="small fw-bold">Payment Method</div>
                    <div class="small text-uppercase">{{ order.payment_method }}</div>
                </div>
            </div>
        </div>

        <div class="mt-4">
            <a href="{% url 'adminpanel:orders' %}" class="btn btn-outline-secondary w-100 rounded-pill">
                <i data-lucide="arrow-left" size="16" class="me-2"></i> Back to Orders
            </a>
        </div>
    </div>
</div>
{% endblock %}
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully wrote {len(content)} characters to {file_path}")
